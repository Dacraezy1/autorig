"""
Notification system for AutoRig.
Provides various notification mechanisms for long-running operations.
"""

import platform
import subprocess
from typing import Optional


class NotificationManager:
    """
    Manages different notification systems based on the platform.
    """

    def __init__(self):
        self.system = platform.system().lower()
        self._available = self._check_notifications_available()

    def _check_notifications_available(self) -> bool:
        """
        Check if notifications are available on the current system.
        """
        if self.system == "darwin":  # macOS
            try:
                # Check if terminal-notifier is available
                subprocess.run(
                    ["which", "terminal-notifier"], capture_output=True, check=True
                )
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Check if osascript is available (built-in)
                try:
                    subprocess.run(
                        ["osascript", "-e", 'display notification "test"'],
                        capture_output=True,
                        check=True,
                    )
                    return True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    return False
        elif self.system in ["linux", "freebsd"]:  # Linux or other Unix-like
            try:
                subprocess.run(
                    ["which", "notify-send"], capture_output=True, check=True
                )
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                return False
        elif self.system == "windows":
            try:
                import importlib.util

                # Check if win10toast is available
                win10toast_spec = importlib.util.find_spec("win10toast")
                if win10toast_spec is not None:
                    return True
                else:
                    return False
            except (ImportError, AttributeError):
                return False
        else:
            return False

    def send_notification(
        self, title: str, message: str, duration: int = 5, icon: Optional[str] = None
    ):
        """
        Send a notification with the given title and message.
        """
        if not self._available:
            return

        try:
            if self.system == "darwin":  # macOS
                self._send_macos_notification(title, message, duration, icon)
            elif self.system in ["linux", "freebsd"]:  # Linux
                self._send_linux_notification(title, message, duration, icon)
            elif self.system == "windows":  # Windows
                self._send_windows_notification(title, message, duration, icon)
        except Exception:
            # Don't let notification errors affect the main functionality
            pass

    def _send_macos_notification(
        self, title: str, message: str, duration: int, icon: Optional[str]
    ):
        """
        Send notification on macOS using osascript or terminal-notifier.
        """
        try:
            # Try terminal-notifier first (more features)
            cmd = [
                "terminal-notifier",
                "-title",
                title,
                "-message",
                message,
                "-timeout",
                str(duration),
            ]
            if icon:
                cmd.extend(["-appIcon", icon])

            subprocess.run(cmd, check=False)
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fallback to osascript
            script = f'display notification "{message}" with title "{title}"'
            subprocess.run(["osascript", "-e", script], check=False)

    def _send_linux_notification(
        self, title: str, message: str, duration: int, icon: Optional[str]
    ):
        """
        Send notification on Linux using notify-send.
        """
        cmd = [
            "notify-send",
            title,
            message,
            f"--expire-time={duration * 1000}",  # Convert to milliseconds
        ]

        if icon:
            cmd.extend(["--icon", icon])

        subprocess.run(cmd, check=False)

    def _send_windows_notification(
        self, title: str, message: str, duration: int, icon: Optional[str]
    ):
        """
        Send notification on Windows using win10toast.
        """
        try:
            import importlib

            win10toast_module = importlib.import_module("win10toast")
            ToastNotifier = getattr(win10toast_module, "ToastNotifier")

            toaster = ToastNotifier()
            toaster.show_toast(
                title=title,
                msg=message,
                duration=duration,
                icon_path=icon if icon else None,
                threaded=True,
            )
        except (ImportError, AttributeError):
            pass  # Notification library not available
        except Exception:
            pass  # Other error in notification


class ProgressTracker:
    """
    Tracks progress of long-running operations and can send notifications.
    """

    def __init__(self, notification_manager: Optional[NotificationManager] = None):
        self.notification_manager = notification_manager or NotificationManager()
        self.total_steps = 0
        self.current_step = 0
        self.operation_name = ""

    def start_operation(self, operation_name: str, total_steps: int):
        """
        Start tracking an operation with the specified number of steps.
        """
        self.operation_name = operation_name
        self.total_steps = total_steps
        self.current_step = 0

        # Send initial notification
        self.notification_manager.send_notification(
            "AutoRig Operation Started",
            f"Starting: {operation_name} ({total_steps} steps)",
            duration=3,
        )

    def update_progress(self, step_description: str = ""):
        """
        Update progress to the next step.
        """
        self.current_step += 1
        progress_percent = int((self.current_step / self.total_steps) * 100)

        message = f"{self.operation_name}: {self.current_step}/{self.total_steps} ({progress_percent}%)"
        if step_description:
            message += f" - {step_description}"

        # Send notification every 25% progress or at the beginning/end
        if (
            progress_percent % 25 == 0
            or self.current_step == 1
            or self.current_step == self.total_steps
        ):
            self.notification_manager.send_notification(
                "AutoRig Progress Update", message, duration=2
            )

    def complete_operation(self):
        """
        Complete the current operation and send final notification.
        """
        self.notification_manager.send_notification(
            "AutoRig Operation Complete",
            f"Completed: {self.operation_name}",
            duration=5,
        )
        # Reset values
        self.total_steps = 0
        self.current_step = 0
        self.operation_name = ""

    def fail_operation(self, error_message: str = ""):
        """
        Mark operation as failed and send notification.
        """
        msg = f"Failed: {self.operation_name}"
        if error_message:
            msg += f" - {error_message}"

        self.notification_manager.send_notification(
            "AutoRig Operation Failed", msg, duration=10
        )
