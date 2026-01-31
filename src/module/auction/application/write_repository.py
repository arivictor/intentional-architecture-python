from typing import Protocol

from module.auction.domain.entity import Auction
from module.auction.domain.value_object import AuctionID


class AuctionWriteRepository(Protocol):
    """Repository interface for Auction aggregate root (Write Side)."""

    seen_entities: list[Auction]

    def save(self, auction: Auction) -> None: ...
    def find_by_id(self, auction_id: AuctionID) -> Auction | None: ...
