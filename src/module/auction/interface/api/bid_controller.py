from typing import Any

from module.auction.application.command import PlaceBidCommand
from module.auction.application.command_handler import PlaceBidHandler
from module.auction.application.query import ListBidsQuery
from module.auction.infrastructure.sqlite_auction_unit_of_work import SQLiteAuctionUnitOfWork
from shared.application.event_bus import EventBus
from shared.application.query_bus import QueryBus


class BidController:
    def __init__(self, query_bus: QueryBus, uow_factory: type[SQLiteAuctionUnitOfWork], event_bus: EventBus, db_path: str):
        self.query_bus = query_bus
        self.uow_factory = uow_factory
        self.event_bus = event_bus
        self.db_path = db_path

    # GET /auctions/{id}/bids
    def list_bids(self, body: dict[str, Any] | None, params: dict[str, str]) -> tuple[int, Any]:
        result = self.query_bus.dispatch(ListBidsQuery(auction_id=params["id"]))
        if result is not None:
            return 200, {
                "items": result,
                "_links": {
                    "self": {"href": f"/auctions/{params['id']}/bids", "method": "GET"},
                    "auction": {"href": f"/auctions/{params['id']}", "method": "GET"},
                },
            }
        return 404, {"error": "Auction not found"}

    # POST /auctions/{id}/bids
    def place_bid(self, body: dict[str, Any] | None, params: dict[str, str]) -> tuple[int, Any]:
        if not body:
            return 400, {"error": "Missing body"}

        # Validate request body
        bidder_id = body.get("bidder_id")
        amount = body.get("amount")
        if bidder_id is None or amount is None:
            return 400, {"error": "Missing required fields: bidder_id and amount"}

        cmd = PlaceBidCommand(auction_id=params["id"], bidder_id=bidder_id, amount=float(amount))

        uow = self.uow_factory(self.event_bus, db_path=self.db_path)
        handler = PlaceBidHandler(uow)
        handler.handle(cmd)

        return 200, {
            "message": "Bid accepted",
            "_links": {
                "auction": {"href": f"/auctions/{params['id']}", "method": "GET"},
                "bids": {"href": f"/auctions/{params['id']}/bids", "method": "GET"},
            },
        }
