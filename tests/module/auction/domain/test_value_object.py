from module.auction.domain.value_object import AuctionID, Bid


def test_bid_value_object():
    bid1 = Bid(bidder_id="bidder1", amount=100.0)
    bid2 = Bid(bidder_id="bidder1", amount=100.0)
    bid3 = Bid(bidder_id="bidder2", amount=150.0)

    # Test equality
    assert bid1 == bid2
    assert bid1 != bid3

    # Test attributes
    assert bid1.bidder_id == "bidder1"
    assert bid1.amount == 100.0


def test_auction_id_generation():
    id1 = AuctionID.generate()
    id2 = AuctionID.generate()

    assert isinstance(id1.value, str)
    assert len(id1.value) > 0
    assert id1 != id2


def test_auction_id_equality():
    id1 = AuctionID(value="test-uuid")
    id2 = AuctionID(value="test-uuid")
    id3 = AuctionID(value="other-uuid")

    assert id1 == id2
    assert id1 != id3
