import pytest

from module.auction.domain.entity import Auction
from module.auction.domain.event import BidPlaced
from module.auction.domain.exception import AuctionException
from module.auction.domain.value_object import Bid


def test_auction_initialization():
    item_id = "item-123"
    starting_price = 10.0
    auction = Auction(item_id, starting_price)

    assert auction.item_id == item_id
    assert auction.starting_price == starting_price
    assert auction.bids == []
    assert auction.events == []
    assert auction.is_active is True
    assert auction.current_price == starting_price
    assert auction.id is not None
    assert auction.id.value is not None


def test_place_bid_successfully():
    auction = Auction("item-123", 10.0)
    bidder_id = "bidder-1"
    amount = 15.0

    auction.place_bid(bidder_id, amount)

    assert len(auction.bids) == 1
    assert auction.bids[0] == Bid(bidder_id, amount)
    assert auction.current_price == amount

    # Check Event
    assert len(auction.events) == 1
    event = auction.events[0]
    assert isinstance(event, BidPlaced)
    assert event.auction_id == auction.id.value
    assert event.bidder_id == bidder_id
    assert event.amount == amount


def test_place_higher_bid():
    auction = Auction("item-123", 10.0)
    auction.place_bid("bidder-1", 15.0)

    # Place a higher bid
    auction.place_bid("bidder-2", 20.0)

    assert len(auction.bids) == 2
    assert auction.current_price == 20.0
    assert len(auction.events) == 2  # one for each bid


def test_cannot_place_lower_bid():
    auction = Auction("item-123", 10.0)

    # Try to bid lower than starting price
    with pytest.raises(AuctionException) as excinfo:
        auction.place_bid("bidder-fail", 5.0)
    assert "higher than current price" in str(excinfo.value)

    # Place a valid bid
    auction.place_bid("bidder-1", 15.0)

    # Try to bid lower than current highest bid
    with pytest.raises(AuctionException) as excinfo:
        auction.place_bid("bidder-fail", 12.0)
    assert "higher than current price" in str(excinfo.value)

    # Try to bid equal to current price
    with pytest.raises(AuctionException) as excinfo:
        auction.place_bid("bidder-fail", 15.0)
    assert "higher than current price" in str(excinfo.value)


def test_cannot_bid_on_closed_auction():
    auction = Auction("item-123", 10.0)
    auction.is_active = False

    with pytest.raises(AuctionException) as excinfo:
        auction.place_bid("bidder-1", 20.0)
    assert "Auction is closed" in str(excinfo.value)
