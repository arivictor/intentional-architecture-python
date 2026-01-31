import logging
import sqlite3
from types import TracebackType

from module.auction.application.unit_of_work import AuctionUnitOfWork
from module.auction.application.write_repository import AuctionWriteRepository
from module.auction.infrastructure.sqlite_auction_write_repository import SQLiteAuctionWriteRepository
from shared.application.event_bus import EventBus

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class SQLiteAuctionUnitOfWork(AuctionUnitOfWork):
    def __init__(self, event_bus: EventBus, db_path: str = "auctions.db"):
        self.event_bus = event_bus
        self.db_path = db_path
        self.connection: sqlite3.Connection | None = None
        self.repo: AuctionWriteRepository = None  # type: ignore

    def __enter__(self) -> "AuctionUnitOfWork":
        self.connection = sqlite3.connect(self.db_path)
        # Use the tracking repo so UoW can see the entities
        self.repo = SQLiteAuctionWriteRepository(self.connection)
        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: TracebackType | None) -> None:
        super().__exit__(exc_type, exc_value, traceback)
        if self.connection:
            self.connection.close()

    def commit(self):
        # 1. Collect events from ALL loaded entities in the repo
        # Use the 'seen_entities' list which tracks objects loaded or saved by the repo
        for auction in self.repo.seen_entities:
            if auction.events:
                self.event_bus.publish(list(auction.events))
                auction.events.clear()

        if self.connection:
            self.connection.commit()
        logger.info("✅ UoW Committed: Database updated & Events published.")

    def rollback(self):
        if self.connection:
            self.connection.rollback()
        logger.warning("🛑 UoW Rolled back due to error.")
