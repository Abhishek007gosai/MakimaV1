"""
Minimal HTTP health endpoint for Koyeb / Render / Railway.
Listens on $PORT (default 8080) so platform health checks pass.
Runs in a background daemon thread – does not block the bot.
"""
import logging
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

logger = logging.getLogger(__name__)


class _HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"ok")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        pass


def start_health_server(port: int | None = None) -> None:
    if port is None:
        raw = os.getenv("PORT") or os.getenv("HEALTH_PORT") or "8080"
        try:
            port = int(raw)
        except ValueError:
            port = 8080

    if port <= 0:
        logger.info("Health server disabled (PORT<=0)")
        return

    def _run():
        try:
            server = HTTPServer(("0.0.0.0", port), _HealthHandler)
            logger.info(f"Health server listening on 0.0.0.0:{port}")
            server.serve_forever()
        except OSError as e:
            # Port already in use – non-fatal on some platforms
            logger.warning(f"Health server could not bind :{port}: {e}")
        except Exception as e:
            logger.warning(f"Health server failed: {e}")

    t = threading.Thread(target=_run, name="health-server", daemon=True)
    t.start()
