import logging
from http.server import HTTPServer
from socketserver import ThreadingMixIn

from interface.api.router import Router

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

    pass


def run_server(port: int = 8000):
    server_address = ("", port)
    httpd = ThreadingHTTPServer(server_address, Router)
    logger.info(f"🚀 Server starting on http://localhost:{port}")
    httpd.serve_forever()
