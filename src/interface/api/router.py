import json
import logging
import os
from http.server import BaseHTTPRequestHandler
from typing import Any
from urllib.parse import urlparse

from interface.api.bootstrap import bootstrap_dependencies
from module.auction.infrastructure.sqlite_auction_unit_of_work import SQLiteAuctionUnitOfWork
from module.auction.interface.api.auction_controller import AuctionController
from module.auction.interface.api.bid_controller import BidController
from shared.domain.exception import DomainException

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DB_PATH = os.getenv("DB_PATH", "auctions.db")


class Router(BaseHTTPRequestHandler):
    # Dependencies
    event_bus, _, query_bus = bootstrap_dependencies(DB_PATH)

    # Initialize Controllers
    auction_ctrl = AuctionController(query_bus, SQLiteAuctionUnitOfWork, event_bus, DB_PATH)
    bid_ctrl = BidController(query_bus, SQLiteAuctionUnitOfWork, event_bus, DB_PATH)

    def _send_response(self, status_code: int, data: Any = None, content_type: str = "application/json"):
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        if data is not None:
            if content_type == "application/json":
                self.wfile.write(json.dumps(data).encode("utf-8"))
            else:
                self.wfile.write(data.encode("utf-8"))

    def _parse_body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}

        # Determine content type to parse form data vs json
        if self.headers.get("Content-Type") == "application/x-www-form-urlencoded":
            from urllib.parse import parse_qs

            data = self.rfile.read(length).decode("utf-8")
            parsed = parse_qs(data)
            # Flatten lists from parse_qs
            return {k: v[0] for k, v in parsed.items()}

        try:
            return json.loads(self.rfile.read(length))
        except json.JSONDecodeError:
            return {}

    def do_GET(self):
        try:
            parsed = urlparse(self.path)
            path_parts = parsed.path.strip("/").split("/")

            # Router Logic
            status, data = 404, {"error": "Not Found"}

            # API Routes
            # GET /
            if parsed.path == "/":
                status, data = 200, {
                    "message": "Welcome to the Auction Service API",
                    "_links": {
                        "self": {"href": "/", "method": "GET"},
                        "auctions": {"href": "/auctions", "method": "GET"},
                        "create_auction": {"href": "/auctions", "method": "POST"},
                    },
                }

            # GET /auctions
            elif parsed.path == "/auctions":
                status, data = self.auction_ctrl.list_auctions(None, {})

            # GET /auctions/{id}
            elif len(path_parts) == 2 and path_parts[0] == "auctions":
                status, data = self.auction_ctrl.get_auction(None, {"id": path_parts[1]})

            # GET /auctions/{id}/bids
            elif len(path_parts) == 3 and path_parts[0] == "auctions" and path_parts[2] == "bids":
                status, data = self.bid_ctrl.list_bids(None, {"id": path_parts[1]})

            self._send_response(status, data)

        except Exception as e:
            logger.exception("GET Request failed")
            self._send_response(500, {"error": str(e)}, "application/json")

    def do_POST(self):
        try:
            parsed = urlparse(self.path)
            path_parts = parsed.path.strip("/").split("/")
            body = self._parse_body()

            # Router Logic
            status, data = 404, {"error": "Not Found"}

            # POST /auctions
            if parsed.path == "/auctions":
                status, data = self.auction_ctrl.create_auction(body, {})

            # POST /auctions/{id}/bids
            elif len(path_parts) == 3 and path_parts[0] == "auctions" and path_parts[2] == "bids":
                status, data = self.bid_ctrl.place_bid(body, {"id": path_parts[1]})

            self._send_response(status, data)

        except DomainException as e:
            self._send_response(400, {"error": str(e), "type": "BusinessRuleViolation"})
        except Exception as e:
            logger.exception("POST Request failed")
            self._send_response(500, {"error": str(e)})
