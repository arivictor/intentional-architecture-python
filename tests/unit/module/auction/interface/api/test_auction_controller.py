from unittest.mock import MagicMock

from module.auction.infrastructure.sqlite_auction_unit_of_work import SQLiteAuctionUnitOfWork
from module.auction.interface.api.auction_controller import AuctionController
from shared.application.event_bus import EventBus
from shared.application.query_bus import QueryBus


def test_auction_controller_get_auction_links():
    query_bus = MagicMock(spec=QueryBus)
    event_bus = MagicMock(spec=EventBus)
    uow_factory = MagicMock(spec=SQLiteAuctionUnitOfWork)

    controller = AuctionController(query_bus, uow_factory, event_bus, "db.db")

    # Mock query result
    auction_data = {"id": "123", "item_id": "item-1", "price": 100}
    query_bus.dispatch.return_value = auction_data

    status, result = controller.get_auction(None, {"id": "123"})

    assert status == 200
    assert result["id"] == "123"
    assert "_links" in result
    assert result["_links"]["self"]["href"] == "/auctions/123"
    assert result["_links"]["bids"]["href"] == "/auctions/123/bids"


def test_auction_controller_list_auctions_links():
    query_bus = MagicMock(spec=QueryBus)
    controller = AuctionController(query_bus, MagicMock(), MagicMock(), "db.db")

    # Mock query result
    auctions = [{"id": "1", "item_id": "i1"}, {"id": "2", "item_id": "i2"}]
    query_bus.dispatch.return_value = auctions

    status, result = controller.list_auctions(None, {})

    assert status == 200
    assert len(result) == 2
    assert result[0]["_links"]["self"]["href"] == "/auctions/1"
    assert result[1]["_links"]["self"]["href"] == "/auctions/2"
