from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from single_instance import check_single_instance
from pathlib import Path
import traceback
import threading
import signal
import socket
import json
import sys
import os

APP_VERSION = "1.0.0"

_CONFIG_FILE = Path(__file__).parent / "config.json"

def _load_config() -> dict:
    # When frozen, prefer config.json next to the exe (user-editable),
    # fall back to the bundled copy inside the extracted temp dir.
    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).parent
        candidate = exe_dir / "config.json"
        if candidate.exists():
            config_path = candidate
        else:
            config_path = Path(sys._MEIPASS) / "config.json"
    else:
        config_path = _CONFIG_FILE
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except Exception:
        return {}

_config = _load_config()
HOST = _config.get("host", "0.0.0.0")
PORT = int(_config.get("port", 5005))


class NoCacheHandler(SimpleHTTPRequestHandler):
    _base: Path = Path(".")   # set before server starts

    def do_GET(self):
        # Inject APP_VERSION into index.html at serve time
        if self.path in ("/", "/index.html"):
            html = (NoCacheHandler._base / "index.html").read_text(encoding="utf-8")
            html = html.replace("{{VERSION}}", APP_VERSION)
            body = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def log_message(self, format, *args):
        pass  # silence request logs


def get_local_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"


def _write_crash_log() -> None:
    log_path = Path(os.path.expanduser("~")) / "phantom-clock-crash.log"
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(traceback.format_exc())
    print(f"Crash log written to: {log_path}")


if __name__ == "__main__":
    try:
        check_single_instance(PORT)

        # Support both normal execution and PyInstaller onefile bundle
        if getattr(sys, "frozen", False):
            base_dir = Path(sys._MEIPASS)
        else:
            base_dir = Path(__file__).parent

        NoCacheHandler._base = base_dir
        os.chdir(base_dir)  # needed for SimpleHTTPRequestHandler static file fallback

        server = ThreadingHTTPServer((HOST, PORT), NoCacheHandler)

        local_url   = f"http://127.0.0.1:{PORT}"
        network_url = f"http://{get_local_ip()}:{PORT}"

        print(f"Phantom Clock v{APP_VERSION}")
        print(f"Serving on:")
        print(f"  Local:   {local_url}")
        print(f"  Network: {network_url}")
        print("Press Ctrl+C to stop.")

        # Shutdown on SIGINT (Ctrl+C), SIGTERM, and SIGBREAK (console window close)
        def _stop(signum=None, frame=None):
            threading.Thread(target=server.shutdown, daemon=True).start()

        signal.signal(signal.SIGINT,  _stop)
        signal.signal(signal.SIGTERM, _stop)
        if hasattr(signal, "SIGBREAK"):       # Windows console close event
            signal.signal(signal.SIGBREAK, _stop)

        server.serve_forever()

    except Exception:
        _write_crash_log()
        sys.exit(1)

