import pytest

from module.auction.application.command import CreateAuctionCommand, PlaceBidCommand
from module.auction.application.command_handler import CreateAuctionHandler, PlaceBidHandler
from module.auction.application.unit_of_work import AuctionUnitOfWork
from module.auction.application.write_repository import AuctionWriteRepository
from module.auction.domain.entity import Auction
from module.auction.domain.exception import AuctionException
from module.auction.domain.value_object import AuctionID


class MockAuctionWriteRepository(AuctionWriteRepository):
    def __init__(self):
        self.seen_entities = []
        self.auctions = {}
        self.save_called = False
        self.saved_auction = None

    def save(self, auction: Auction) -> None:
        self.save_called = True
        self.saved_auction = auction
        self.auctions[auction.id.value] = auction

    def find_by_id(self, auction_id: AuctionID) -> Auction | None:
        return self.auctions.get(auction_id.value)


class MockAuctionUnitOfWork(AuctionUnitOfWork):
    def __init__(self, repo):
        self.repo = repo
        self.committed = False
        self.rolled_back = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            self.rollback()
        else:
            self.commit()

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True


def test_create_auction_handler():
    repo = MockAuctionWriteRepository()
    uow = MockAuctionUnitOfWork(repo)
    handler = CreateAuctionHandler(uow)

    cmd = CreateAuctionCommand(item_id="item-1", starting_price=10.0)
    auction_id = handler.handle(cmd)

    assert auction_id is not None
    assert repo.save_called is True
    assert repo.saved_auction.item_id == "item-1"
    assert repo.saved_auction.starting_price == 10.0
    assert uow.committed is True
    assert uow.rolled_back is False


def test_place_bid_handler_success():
    repo = MockAuctionWriteRepository()
    uow = MockAuctionUnitOfWork(repo)

    # Setup existing auction
    existing_auction = Auction("item-1", 10.0)
    repo.save(existing_auction)
    repo.save_called = False  # Reset for test
    uow.committed = False

    handler = PlaceBidHandler(uow)
    cmd = PlaceBidCommand(auction_id=existing_auction.id.value, bidder_id="bidder-1", amount=20.0)

    handler.handle(cmd)

    # Verify bid placed
    loaded_auction = repo.auctions[existing_auction.id.value]
    assert len(loaded_auction.bids) == 1
    assert loaded_auction.bids[0].amount == 20.0
    assert repo.save_called is True
    assert uow.committed is True


def test_place_bid_handler_auction_not_found():
    repo = MockAuctionWriteRepository()
    uow = MockAuctionUnitOfWork(repo)
    handler = PlaceBidHandler(uow)

    cmd = PlaceBidCommand(auction_id="non-existent", bidder_id="bidder-1", amount=20.0)

    with pytest.raises(AuctionException) as excinfo:
        handler.handle(cmd)

    assert "Auction not found" in str(excinfo.value)
    # The UoW handles the exception in __exit__ by rolling back
    assert uow.rolled_back is True
    assert uow.committed is False


def test_place_bid_handler_domain_rule_violation():
    repo = MockAuctionWriteRepository()
    uow = MockAuctionUnitOfWork(repo)

    # Auction with high bid
    existing_auction = Auction("item-1", 100.0)
    repo.save(existing_auction)

    handler = PlaceBidHandler(uow)
    # Bid too low
    cmd = PlaceBidCommand(auction_id=existing_auction.id.value, bidder_id="bidder-1", amount=50.0)

    with pytest.raises(AuctionException) as excinfo:
        handler.handle(cmd)

    assert "must be higher" in str(excinfo.value)
    assert uow.rolled_back is True
