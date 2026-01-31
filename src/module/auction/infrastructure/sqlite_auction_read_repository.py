import json
import sqlite3
from typing import Any

from module.auction.application.read_repository import AuctionReadRepository


class SQLiteAuctionReadRepository(AuctionReadRepository):
    """
    Infrastructure implementation of the Read Repository using SQLite.
    Bypasses the Domain Model for performance and returns simple DTOs (dicts).
    """

    def __init__(self, db_path: str):
        self.db_path = db_path

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Access columns by name
        return conn

    def list_auctions(self) -> list[dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, item_id, starting_price, is_active FROM auctions")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_auction(self, auction_id: str) -> dict[str, Any] | None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM auctions WHERE id = ?", (auction_id,))
            row = cursor.fetchone()
            if not row:
                return None

            data = dict(row)
            # Parse JSON bids
            if data.get("bids"):
                data["bids"] = json.loads(data["bids"])
            else:
                data["bids"] = []

            data["is_active"] = bool(data["is_active"])
            return data

    def list_bids(self, auction_id: str) -> list[dict[str, Any]] | None:
        auction = self.get_auction(auction_id)
        if not auction:
            return None
        return auction.get("bids", [])
