# ruff: noqa
# type: ignore
import argparse
import logging
import subprocess
import time

from ppadb.client import Client as AdbClient

logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)


class AndroidPositionTester:
    def __init__(self, device):
        self.device = device
        self.device_serial = device.get_serial_no()
        # Get device screen dimensions
        screen_size = self.device.shell("wm size").strip()
        width, height = map(int, screen_size.split()[-1].split("x"))
        self.screen_width = width
        self.screen_height = height
        _LOGGER.info(f"Device screen size: {width}x{height}")
        # Start coordinate tracking
        self.start_coordinate_tracking()

    def start_coordinate_tracking(self):
        """Start tracking touch coordinates."""
        try:
            # Clear the event buffer
            subprocess.run(["adb", "-s", self.device_serial, "s6hell", "getevent -c"], check=True)
            # Start tracking in background
            self.tracking_process = subprocess.Popen(
                ["adb", "-s", self.device_serial, "shell", "getevent -l"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            _LOGGER.info("Coordinate tracking started")
        except subprocess.CalledProcessError as e:
            _LOGGER.error(f"Failed to start coordinate tracking: {e}")

    def get_touch_coordinates(self) -> tuple[int, int] | None:
        """Get the coordinates of the last touch event."""
        try:
            x, y = None, None
            while True:
                line = self.tracking_process.stdout.readline()
                if not line:
                    break
                if "ABS_MT_POSITION_X" in line:
                    x = int(line.split()[-1], 16)
                elif "ABS_MT_POSITION_Y" in line:
                    y = int(line.split()[-1], 16)
                if x is not None and y is not None:
                    return x, y
            return None
        except Exception as e:
            _LOGGER.error(f"Error reading coordinates: {e}")
            return None

    def tap_position(self, x_ratio: float, y_ratio: float) -> None:
        """Tap a position specified by ratios of screen dimensions."""
        x = int(self.screen_width * x_ratio)
        y = int(self.screen_height * y_ratio)
        cmd = f"input tap {x} {y}"
        _LOGGER.info(f"Tapping at position: x={x} ({x_ratio:.4f}), y={y} ({y_ratio:.4f})")
        self.device.shell(cmd)

    def test_positions(self):
        """Interactive testing of different positions."""
        while True:
            try:
                action = input(
                    "\nChoose action to test:\n"
                    "1. Share button\n"
                    "2. Like button\n"
                    "3. Comment button\n"
                    "4. Copy link button\n"
                    "5. Post button\n"
                    "6. Follow button\n"
                    "7. Input text\n"
                    "8. Custom position\n"
                    "9. Show current ratios\n"
                    "10. Find coordinates (touch screen)\n"
                    "11. Calculate ratios from coordinates\n"
                    "q. Quit\n"
                    "Choice: "
                ).strip()

                if action == "q":
                    break

                if action == "10":
                    x = int(input("Enter x coordinate: "))
                    y = int(input("Enter y coordinate: "))
                    x_ratio = x / self.screen_width
                    y_ratio = y / self.screen_height
                    print("\nCalculated ratios:")
                    print(f"X: {x} (ratio: {x_ratio:.4f})")
                    print(f"Y: {y} (ratio: {y_ratio:.4f})")
                    print("\nFor android_bot.py:")
                    print(f"BUTTON_X = {x_ratio:.4f}  # {x}/{self.screen_width}")
                    print(f"BUTTON_Y = {y_ratio:.4f}  # {y}/{self.screen_height}")
                    continue

                if action == "8":
                    x_ratio = float(input("Enter x ratio (0-1): "))
                    y_ratio = float(input("Enter y ratio (0-1): "))
                    self.tap_position(x_ratio, y_ratio)
                    continue

                if action == "9":
                    print("\nCurrent normalized ratios:")
                    print(f"SHARE_BUTTON_X = {0.9375}  # 1200/1280")
                    print(f"SHARE_BUTTON_Y = {0.798}   # 2280/2856")
                    print(f"LIKE_BUTTON_X = {0.9375}   # 1200/1280")
                    print(f"LIKE_BUTTON_Y = {0.602}    # 1720/2856")
                    print(f"COMMENT_BUTTON_X = {0.9375}# 1200/1280")
                    print(f"COMMENT_BUTTON_Y = {0.672} # 1920/2856")
                    continue

                if action == "10":
                    print("Touch the screen where you want to measure coordinates...")
                    coords = self.get_touch_coordinates()
                    if coords:
                        x, y = coords
                        x_ratio = x / self.screen_width
                        y_ratio = y / self.screen_height
                        print("\nTouch coordinates:")
                        print(f"X: {x} (ratio: {x_ratio:.4f})")
                        print(f"Y: {y} (ratio: {y_ratio:.4f})")
                        print("\nFor android_bot.py:")
                        print(f"BUTTON_X = {x_ratio:.4f}  # {x}/{self.screen_width}")
                        print(f"BUTTON_Y = {y_ratio:.4f}  # {y}/{self.screen_height}")
                    continue

                # Predefined positions to test
                positions = {
                    "1": (0.9375, 0.798),  # Share
                    "2": (0.9375, 0.602),  # Like
                    "3": (0.9375, 0.672),  # Comment
                    "4": (0.25, 0.8123),  # Copy link
                    "5": (0.9219, 0.6232),  # Post
                    "6": (0.9297, 0.5602),  # Follow
                    "7": (0.2570, 0.9454),  # Input text
                }

                if action in positions:
                    x_ratio, y_ratio = positions[action]
                    self.tap_position(x_ratio, y_ratio)
                    time.sleep(1)  # Wait a bit between taps

            except ValueError as e:
                _LOGGER.error(f"Invalid input: {e}")
            except KeyboardInterrupt:
                break


def main():
    parser = argparse.ArgumentParser(description="Test Android UI positions")
    parser.add_argument("--device", help="Device serial number (optional)")
    args = parser.parse_args()

    # Connect to ADB
    adb_client = AdbClient(host="127.0.0.1", port=5037)

    if args.device:
        device = adb_client.device(args.device)
        if not device:
            _LOGGER.error(f"Device {args.device} not found!")
            return
    else:
        devices = adb_client.devices()
        if not devices:
            _LOGGER.error("No ADB devices found!")
            return
        device = devices[0]
        _LOGGER.info(f"Using device: {device.get_serial_no()}")

    try:
        tester = AndroidPositionTester(device)
        tester.test_positions()
    finally:
        # Clean up the tracking process
        if hasattr(tester, "tracking_process"):
            tester.tracking_process.terminate()


if __name__ == "__main__":
    main()
