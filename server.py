from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import webbrowser
import socket
import os

PORT = 5005


class NoCacheHandler(SimpleHTTPRequestHandler):
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


if __name__ == "__main__":
    os.chdir(Path(__file__).parent)

    server = ThreadingHTTPServer(("0.0.0.0", PORT), NoCacheHandler)

    local_url = f"http://127.0.0.1:{PORT}"
    network_url = f"http://{get_local_ip()}:{PORT}"

    print(f"Serving on:")
    print(f"  Local:   {local_url}")
    print(f"  Network: {network_url}")
    print("Press Ctrl+C to stop.")

    server.serve_forever()

