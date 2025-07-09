# mypy: disable-error-code="no-untyped-call"
import gzip
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

import brotli

f = open(
    Path(__file__).parent / f"output_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt",
    "w",
    encoding="utf-8",
)


def decode_protobuf_raw(content: bytes) -> str:
    """Decode the protobuf response."""
    try:
        # call protoc --decode_raw with the response bytes
        result = subprocess.run(["protoc", "--decode_raw"], input=content, capture_output=True)
        return result.stdout.decode("utf-8", errors="replace")
    except Exception as e:
        return f"Error decoding protobuf: {e}"


def decode_content(content: bytes, headers: dict[str, str]) -> str:
    """Decode the content of the request or response."""
    new_content = content
    if headers.get("content-encoding") == "gzip":
        try:
            new_content = gzip.decompress(content)
        except Exception as e:
            print(f"Error decompressing response: {repr(e)}")

    elif headers.get("x-bd-content-encoding") == "gzip":
        try:
            new_content = gzip.decompress(new_content)
        except Exception as e:
            print(f"Error decompressing response: {repr(e)}")

    if "protobuf" in (headers.get("content-type") or ""):
        # decode the protobuf
        new_content = decode_protobuf_raw(new_content).encode("utf-8")

    if "br" in (headers.get("content-encoding") or ""):
        new_content = brotli.decompress(new_content)

    return new_content


def assemble_request(content, headers, trailers=None):
    if content is None:
        raise ValueError("Cannot assemble flow with missing content")
    head = assemble_request_head(headers)
    body = b"".join(assemble_body(headers, [content], trailers))
    return head + body


def assemble_request_head(headers):
    first_line = _assemble_request_line(headers)
    headers_bytes = _assemble_request_headers(headers)
    return b"%s\r\n%s\r\n" % (first_line, headers_bytes)


def assemble_response(content, headers, trailers=None):
    if content is None:
        raise ValueError("Cannot assemble flow with missing content")
    head = assemble_response_head(headers)
    body = b"".join(assemble_body(headers, [content], trailers))
    return head + body


def assemble_response_head(headers):
    first_line = _assemble_response_line(headers)
    headers_bytes = _assemble_response_headers(headers)
    return b"%s\r\n%s\r\n" % (first_line, headers_bytes)


def assemble_body(headers, body_chunks, trailers):
    if "chunked" in headers.get("transfer-encoding", "").lower():
        for chunk in body_chunks:
            if chunk:
                yield b"%x\r\n%s\r\n" % (len(chunk), chunk)
        if trailers:
            yield b"0\r\n%s\r\n" % trailers
        else:
            yield b"0\r\n\r\n"
    else:
        if trailers:
            raise ValueError("Sending HTTP/1.1 trailer headers requires transfer-encoding: chunked")
        for chunk in body_chunks:
            yield chunk


def _assemble_request_line(headers):
    method = headers.get("method", b"GET")
    authority = headers.get("authority")
    http_version = headers.get("http_version", b"HTTP/1.1")
    scheme = headers.get("scheme", b"https")
    path = headers.get("path", b"/")

    if method.upper() == b"CONNECT":
        return b"%s %s %s" % (
            method,
            authority,
            http_version,
        )
    elif authority:
        return b"%s %s://%s%s %s" % (
            method,
            scheme,
            authority,
            path,
            http_version,
        )
    else:
        return b"%s %s %s" % (
            method,
            path,
            http_version,
        )


def _assemble_request_headers(headers):
    return bytes(headers)


def _assemble_response_line(headers):
    http_version = headers.get("http_version", b"HTTP/1.1")
    status_code = int(headers.get("status_code", 200))
    reason = headers.get("reason", b"OK")
    return b"%s %d %s" % (
        http_version,
        status_code,
        reason,
    )


def _assemble_response_headers(headers):
    return bytes(headers)


def response(flow: Any) -> None:
    """
    Function to parse the response and write to the file.
    """
    try:
        # Try to decode the request as UTF-8, skip if not possible
        decoded_request = decode_content(flow.request.content, flow.request.headers)
        request_data = assemble_request(
            decoded_request, flow.request.headers, flow.request.trailers
        ).decode("utf-8", errors="ignore")
        f.write("\n================== REQUEST ==================\n")
        f.write(request_data)
        # If gzip is used, we need to decompress the response
        decoded_response = decode_content(flow.response.data.content, flow.response.headers)
        response_data = assemble_response(
            decoded_response, flow.response.headers, flow.response.trailers
        ).decode("utf-8", errors="ignore")

        f.write("\n================== RESPONSE ==================\n")
        f.write(response_data)
    except Exception as e:
        # Log any errors but don't crash
        raise e


from pathlib import Path

from mitmproxy.net.http.http1.assemble import assemble_request, assemble_response

f = open(Path(__file__).parent / "output.txt", "w", encoding="utf-8")


def decode_protobuf_raw(content: bytes) -> str:
    """Decode the protobuf response."""
    try:
        # call protoc --decode_raw with the response bytes
        result = subprocess.run(["protoc", "--decode_raw"], input=content, capture_output=True)
        return result.stdout.decode("utf-8", errors="replace")
    except Exception as e:
        return f"Error decoding protobuf: {e}"


def response(flow):
    """
    Function to parse the response and write to the file.
    """
    try:
        # Try to decode the request as UTF-8, skip if not possible
        request_data = assemble_request(flow.request).decode("utf-8", errors="ignore")
        f.write(request_data)

        # If gzip is used, we need to decompress the response
        content = flow.response.content
        if flow.response.headers.get("content-encoding") == "gzip":
            try:
                content = gzip.decompress(flow.response.content)
            except Exception as e:
                print(f"Error decompressing response: {repr(e)}")

        is_proto = False
        if "protobuf" in (flow.response.headers.get("content-type") or ""):
            # decode the protobuf
            content = decode_protobuf_raw(content).encode("utf-8")
            is_proto = True
            print(content[:100])

        flow.response.data.content = content

        # Try to decode the response as UTF-8, skip if not possible
        response_data = assemble_response(flow.response).decode("utf-8", errors="ignore")
        if is_proto:
            print(response_data[:100])
        f.write(response_data)
    except Exception as e:
        # Log any errors but don't crash
        print("Content_type: ", type(content))
        print("Content: ", content[:100])
        raise e
