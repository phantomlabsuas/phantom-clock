import os
import socket


EXE_NAME = "phantom-clock.exe"


def is_port_in_use(port: int) -> bool:
    """Return True if something is already listening on the given port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def already_running() -> bool:
    """
    Return True if another phantom-clock process is already running.

    Excludes both the current PID and the parent PID because PyInstaller
    onefile builds spawn two processes with the same exe name:
      - bootloader (parent) — extracts and launches the Python child
      - Python child        — the actual running application

    Without excluding the parent, the child would falsely detect the
    bootloader as a duplicate and refuse to start.

    Falls back silently (returns False) if psutil is not available.
    """
    try:
        import psutil
        current_pid = os.getpid()
        try:
            parent_pid = psutil.Process(current_pid).ppid()
        except Exception:
            parent_pid = -1
        excluded = {current_pid, parent_pid}

        for proc in psutil.process_iter(["pid", "name"]):
            if proc.info["name"] == EXE_NAME and proc.info["pid"] not in excluded:
                return True
        return False
    except ImportError:
        return False


def notify_already_running() -> None:
    """Show a Windows system-modal popup — visible even without a console."""
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(
            0,
            "Phantom Clock is already running.",
            "Phantom Clock",
            0x40 | 0x1000  # MB_ICONINFORMATION | MB_SYSTEMMODAL
        )
    except Exception:
        print("Phantom Clock is already running.")


def check_single_instance(port: int) -> None:
    """
    Run both instance checks and exit if a duplicate is detected.
    Call this early in __main__ before starting any services.
    """
    import sys

    if already_running():
        notify_already_running()
        sys.exit(0)

    if is_port_in_use(port):
        notify_already_running()
        sys.exit(1)
