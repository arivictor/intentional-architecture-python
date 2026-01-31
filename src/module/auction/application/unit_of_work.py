from module.auction.application.write_repository import AuctionWriteRepository
from shared.application.unit_of_work import UnitOfWork


class AuctionUnitOfWork(UnitOfWork):
    """
    Module-specific Unit of Work interface.
    """

    repo: AuctionWriteRepository  # exposing the repo to the handler
