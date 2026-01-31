from module.auction.application.command import CreateAuctionCommand, PlaceBidCommand
from module.auction.application.unit_of_work import AuctionUnitOfWork
from module.auction.domain.entity import Auction
from module.auction.domain.exception import AuctionException
from module.auction.domain.value_object import AuctionID


class PlaceBidHandler:
    """Handler for PlaceBidCommand."""

    def __init__(self, uow: AuctionUnitOfWork):
        self.uow = uow

    def handle(self, command: PlaceBidCommand):
        # 1. Start Transaction
        with self.uow:
            # 2. Retrieve
            auction = self.uow.repo.find_by_id(AuctionID(command.auction_id))
            if not auction:
                raise AuctionException("Auction not found")

            # 3. Domain Logic
            auction.place_bid(command.bidder_id, command.amount)

            # 4. Persist
            self.uow.repo.save(auction)

            # 5. Commit happens automatically on exit of context manager
            # If an exception occurs, rollback happens automatically


class CreateAuctionHandler:
    """Handler for CreateAuctionCommand."""

    def __init__(self, uow: AuctionUnitOfWork):
        self.uow = uow

    def handle(self, command: CreateAuctionCommand) -> str:
        with self.uow:
            auction = Auction(item_id=command.item_id, starting_price=command.starting_price)
            self.uow.repo.save(auction)
            return auction.id.value
