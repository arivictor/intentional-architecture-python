import json
import logging
import sqlite3

from module.auction.application.write_repository import AuctionWriteRepository
from module.auction.domain.entity import Auction, Bid
from module.auction.domain.value_object import AuctionID

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class SQLiteAuctionWriteRepository(AuctionWriteRepository):
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
        self.seen_entities: list[Auction] = []
        self._create_table()

    def _create_table(self):
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auctions (
                id TEXT PRIMARY KEY,
                item_id TEXT,
                starting_price REAL,
                is_active INTEGER,
                bids TEXT
            )
        """)
        # Note: We do NOT commit here, the UoW manages the commit

    def save(self, auction: Auction) -> None:
        cursor = self.connection.cursor()
        # Serialize bids
        bids_data: list[dict[str, str | float]] = [{"bidder_id": b.bidder_id, "amount": b.amount} for b in auction.bids]
        bids_json = json.dumps(bids_data)

        cursor.execute(
            """
            INSERT OR REPLACE INTO auctions (id, item_id, starting_price, is_active, bids)
            VALUES (?, ?, ?, ?, ?)
        """,
            (auction.id.value, auction.item_id, auction.starting_price, 1 if auction.is_active else 0, bids_json),
        )
        self.seen_entities.append(auction)

    def find_by_id(self, auction_id: AuctionID) -> Auction | None:
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, item_id, starting_price, is_active, bids FROM auctions WHERE id = ?", (auction_id.value,))
        row = cursor.fetchone()

        if not row:
            return None

        # Reconstruct the Auction entity
        # We use the constructor but then patch the state to match the DB
        auction = Auction(item_id=row[1], starting_price=row[2])

        # Patch ID (because __init__ generates a new random one)
        auction.id = AuctionID(row[0])
        auction.is_active = bool(row[3])

        # Patch Bids
        bids_data = json.loads(row[4])
        auction.bids = [Bid(b["bidder_id"], b["amount"]) for b in bids_data]

        if auction:
            self.seen_entities.append(auction)
        return auction
