import base64
import logging
from typing import Any, Type, TypeVar

import instructor
from openai import OpenAI
from PIL import Image
from pydantic import BaseModel, Field

_LOGGER = logging.getLogger(__name__)
_T = TypeVar("_T", bound=BaseModel)


class Comment(BaseModel):
    comment: str = Field(description="The comment to be posted on the video.")


class Agent:
    """
    Agent that interacts with OpenAI via the 'instructor' library to determine the correct action.

    This agent sends prompts to OpenAI and expects structured responses based on provided Pydantic models.
    The agent maintains context about its behavior/persona throughout interactions.
    """

    def __init__(
        self,
        openai_client: OpenAI,
        base_prompt: str,
        behavior_context: str,
        image_size: tuple[int, int] = (120, 120),
    ):
        """
        Initialize the agent.

        :param openai_client: OpenAI client used to instantiate the instructor client
        :param base_prompt: Base system prompt that defines the agent's role
        :param behavior_context: Context describing the bot's behavior/persona
        """
        self.client = instructor.from_openai(openai_client)
        self.image_size = image_size
        # Format the base prompt with the behavior context
        self.base_prompt = base_prompt.format(behavior_context=behavior_context)
        _LOGGER.debug(
            "[OpenAI] Initialized agent with base prompt length: %d", len(self.base_prompt)
        )

        # Initialize memory to store past conversation messages.
        self.memory = list[dict[str, str]]()  # Each entry is a dict with "role" and "content"
        # Set maximum allowed tokens for conversation memory.
        self.max_memory_tokens = 1500  # adjust as needed

        def log_exception(exception: Exception) -> None:
            _LOGGER.error("[OpenAI] OpenAI API error: %s", str(exception))

        self.client.on("completion:error", log_exception)

    def _encode_image(self, image_path: str) -> str:
        """Convert an image file to base64 string."""
        try:
            image = Image.open(image_path)
            image.thumbnail(self.image_size)
            image.save(image_path)
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except Exception as e:
            _LOGGER.error("[OpenAI] Failed to encode image: %s", e)
            return ""

    async def decide_action(
        self, prompt: str, output_model: Type[_T], image_path: str | None = None
    ) -> _T | None:
        """
        Determine the next action based on the given prompt using OpenAI via instructor.

        :param prompt: A prompt or instruction to guide the decision process
        :param output_model: The Pydantic model to use for structuring the output
        :param image_path: Optional path to an image file to include in the prompt
        :return: The structured decision based on the output_model
        """
        _LOGGER.info("[OpenAI] Deciding action for: %s", output_model.__name__)
        try:
            structured_prompt = f"""
Your task:
1. Analyze the following input
2. Respond with a valid {output_model.__name__} structure. Its JSON schema: {output_model.model_json_schema()}
3. Ensure all required fields are included

Input: {prompt}

For each video, use the exact 19-digit video_id provided in the prompt (e.g., "7518780802759511318").
Do NOT invent or shorten video IDs. Do NOT use labels like "video1", "video_3", or "action4".
Your response must only include video_ids that were explicitly listed in the prompt.

Remember to structure your response exactly according to the required model format. 
"""
            # Construct the conversation messages including a trimmed version of stored memory.
            messages: Any = [{"role": "system", "content": self.base_prompt}]
            # Trim memory by removing oldest messages until under token limit.
            trimmed_memory = self._trim_memory(self.memory)
            messages.extend(trimmed_memory)

            image_content = []
            # If we have an image, add it to the user message
            if image_path:
                base64_image = self._encode_image(image_path)
                if base64_image:
                    image_content = [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                        }
                    ]

            text_content = [{"type": "text", "text": structured_prompt}]
            messages.append({"role": "user", "content": text_content + image_content})

            # Call completion API using the instructor-patched client
            decision = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=1000,
                response_model=output_model,
                temperature=0.7,
            )

            # update memory
            assistant_response = (
                decision.model_dump_json()
                if hasattr(decision, "model_dump_json")
                else str(decision)
            )
            self.memory.extend(
                [
                    {"role": "user", "content": structured_prompt},
                    {"role": "assistant", "content": assistant_response},
                ]
            )

            return decision

        except Exception as e:
            _LOGGER.error("[OpenAI] Failed to get decision: %s", repr(e))
            return None

    async def generate_comment(self, video_info: dict[str, Any]) -> str | None:
        """
        Generates a comment text by asking the agent.
        """
        prompt = f"""
        REMEMBER: Use only alphanumeric characters and spaces. (Otherwise ADB input command will fail)
        Don't use any other characters.
        Based on your personality, generate a comment for the following video.

        Video: {video_info}
        """
        response = await self.decide_action(prompt, Comment)
        if response is None:
            return None
        return response.comment

    async def close(self) -> None:
        """No client to close when using instructor."""
        _LOGGER.debug("[OpenAI] Closing agent")
        pass

    def clear_memory(self) -> None:
        """
        Clears the conversation memory. This can be used to reset the context.
        """
        self.memory.clear()

    def _estimate_tokens(self, text: str) -> int:
        """
        Roughly estimate the number of tokens in a given text.

        This approximation assumes 1 token ~ 4 characters.
        """
        return len(text) // 4

    def _trim_memory(self, memory: list[dict[str, str]]) -> list[dict[str, str]]:
        """
        Trim the conversation memory by summarizing older messages instead of discarding them.

        :param memory: The full conversation memory list.
        :return: A trimmed version of memory that contains a summary for older messages along with recent messages.
        """
        total_tokens = sum(self._estimate_tokens(msg["content"]) for msg in memory)
        if total_tokens <= self.max_memory_tokens:
            return memory

        # Define a threshold for recent messages: keep as recent messages that sum to at most half the allowed tokens.
        half_max = self.max_memory_tokens // 2
        recent = list[dict[str, str]]()
        recent_tokens = 0
        # Iterate from the end (most recent) backward to accumulate recent messages.
        for msg in reversed(memory):
            est = self._estimate_tokens(msg["content"])
            if recent_tokens + est <= half_max:
                recent_tokens += est
                recent.insert(0, msg)  # Insert at beginning to preserve order.
            else:
                break

        # Older messages are those not included in "recent".
        older = memory[: len(memory) - len(recent)]

        # Summarize the older messages to retain context in a condensed form.
        if older:
            summary = self._summarize_memory_block(older)
            summary_message = {"role": "assistant", "content": summary}
            new_memory = [summary_message] + recent
        else:
            new_memory = recent

        # In case the new_memory is still too large, remove additional messages from the beginning.
        while (
            new_memory
            and sum(self._estimate_tokens(msg["content"]) for msg in new_memory)
            > self.max_memory_tokens
        ):
            new_memory.pop(0)

        return new_memory

    def _summarize_memory_block(self, messages: list[dict[str, str]]) -> str:
        """
        Summarize a block of conversation messages into a concise summary.

        :param messages: List of message dictionaries to be summarized.
        :return: A summarized string capturing the key points of the conversation.
        """

        class _Summary(BaseModel):
            summary: str

        # Combine messages into a single conversation string.
        conversation = "\n".join(f"{msg['role']}: {msg['content']}" for msg in messages)

        summary_prompt = f"Summarize the following conversation concisely, highlighting key points:\n\n{conversation}"

        _LOGGER.info(
            "[OpenAI] Summarizing memory -> [length: %d]",
            len(summary_prompt),
        )

        # Call the completion API to generate a summary.
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": summary_prompt}],
            max_tokens=200,
            temperature=0.5,
            response_model=_Summary,
        )
        summary_text = (
            str(response.model_dump()) if hasattr(response, "model_dump") else str(response)
        )
        return summary_text
