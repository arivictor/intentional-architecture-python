from typing import Any

from module.auction.application.command import CreateAuctionCommand
from module.auction.application.command_handler import CreateAuctionHandler
from module.auction.application.query import GetAuctionQuery, ListAuctionsQuery
from module.auction.infrastructure.sqlite_auction_unit_of_work import SQLiteAuctionUnitOfWork
from shared.application.event_bus import EventBus
from shared.application.query_bus import QueryBus


class AuctionController:
    def __init__(self, query_bus: QueryBus, uow_factory: type[SQLiteAuctionUnitOfWork], event_bus: EventBus, db_path: str):
        self.query_bus = query_bus
        self.uow_factory = uow_factory
        self.event_bus = event_bus
        self.db_path = db_path

    def _add_links(self, auction: dict[str, Any]) -> dict[str, Any]:
        auction_id = auction["id"]
        auction["_links"] = {
            "self": {"href": f"/auctions/{auction_id}", "method": "GET"},
            "bids": {"href": f"/auctions/{auction_id}/bids", "method": "GET"},
            "place_bid": {"href": f"/auctions/{auction_id}/bids", "method": "POST"},
        }
        return auction

    # GET /auctions
    def list_auctions(self, body: dict[str, Any] | None, params: dict[str, str]) -> tuple[int, Any]:
        result = self.query_bus.dispatch(ListAuctionsQuery())
        for auction in result:
            self._add_links(auction)
        return 200, result

    # GET /auctions/{id}
    def get_auction(self, body: dict[str, Any] | None, params: dict[str, str]) -> tuple[int, Any]:
        result = self.query_bus.dispatch(GetAuctionQuery(auction_id=params["id"]))
        if result:
            self._add_links(result)
            return 200, result
        return 404, {"error": "Auction not found"}

    # POST /auctions
    def create_auction(self, body: dict[str, Any] | None, params: dict[str, str]) -> tuple[int, Any]:
        if not body:
            return 400, {"error": "Missing body"}

        # Validate request body
        item_id = body.get("item_id")
        starting_price = body.get("starting_price")
        if item_id is None or starting_price is None:
            return 400, {"error": "Missing required fields: item_id and starting_price"}

        cmd = CreateAuctionCommand(item_id=item_id, starting_price=float(starting_price))

        # Instantiate UoW per request
        uow = self.uow_factory(self.event_bus, db_path=self.db_path)
        handler = CreateAuctionHandler(uow)
        auction_id = handler.handle(cmd)

        return 201, {
            "id": auction_id,
            "message": "Auction created",
            "_links": {
                "self": {"href": f"/auctions/{auction_id}", "method": "GET"},
                "place_bid": {"href": f"/auctions/{auction_id}/bids", "method": "POST"},
            },
        }
