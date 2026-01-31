import logging

from interface.api.server import run_server

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    try:
        run_server()
    except KeyboardInterrupt:
        logger.info("Stopping server...")
