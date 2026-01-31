from unittest.mock import MagicMock

from module.auction.application.query import GetAuctionQuery, ListAuctionsQuery, ListBidsQuery
from module.auction.application.query_handler import GetAuctionHandler, ListAuctionsHandler, ListBidsHandler
from module.auction.application.read_repository import AuctionReadRepository


def test_get_auction_handler():
    # Mock Repository
    repo = MagicMock(spec=AuctionReadRepository)
    expected_data = {"id": "123", "item_id": "item-1", "price": 100}
    repo.get_auction.return_value = expected_data

    handler = GetAuctionHandler(repo)
    result = handler.handle(GetAuctionQuery(auction_id="123"))

    assert result == expected_data
    repo.get_auction.assert_called_once_with("123")


def test_list_auctions_handler():
    repo = MagicMock(spec=AuctionReadRepository)
    expected_list = [{"id": "1"}, {"id": "2"}]
    repo.list_auctions.return_value = expected_list

    handler = ListAuctionsHandler(repo)
    result = handler.handle(ListAuctionsQuery())

    assert result == expected_list
    repo.list_auctions.assert_called_once()


def test_list_bids_handler():
    repo = MagicMock(spec=AuctionReadRepository)
    expected_bids = [{"amount": 10}, {"amount": 20}]
    repo.list_bids.return_value = expected_bids

    handler = ListBidsHandler(repo)
    result = handler.handle(ListBidsQuery(auction_id="123"))

    assert result == expected_bids
    repo.list_bids.assert_called_once_with("123")
