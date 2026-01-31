from unittest.mock import MagicMock

from module.auction.interface.api.bid_controller import BidController
from shared.application.event_bus import EventBus
from shared.application.query_bus import QueryBus


def test_bid_controller_list_bids_structure():
    query_bus = MagicMock(spec=QueryBus)
    controller = BidController(query_bus, MagicMock(), MagicMock(), "db.db")

    # Mock query result
    bids = [{"amount": 10}, {"amount": 20}]
    query_bus.dispatch.return_value = bids

    status, result = controller.list_bids(None, {"id": "123"})

    assert status == 200
    # Expecting wrapped structure now
    assert "items" in result
    assert result["items"] == bids
    assert "_links" in result
    assert result["_links"]["self"]["href"] == "/auctions/123/bids"
    assert result["_links"]["auction"]["href"] == "/auctions/123"


def test_bid_controller_place_bid_response():
    # Setup mocks for command handling
    query_bus = MagicMock(spec=QueryBus)
    event_bus = MagicMock(spec=EventBus)
    uow_factory = MagicMock()
    uow_instance = MagicMock()
    uow_factory.return_value = uow_instance

    controller = BidController(query_bus, uow_factory, event_bus, "db.db")

    body = {"bidder_id": "u1", "amount": 50.0}
    status, result = controller.place_bid(body, {"id": "123"})

    assert status == 200
    assert result["message"] == "Bid accepted"
    assert result["_links"]["auction"]["href"] == "/auctions/123"
