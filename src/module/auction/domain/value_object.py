import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class Bid:
    """Value object representing a bid in an auction."""

    bidder_id: str
    amount: float


@dataclass(frozen=True)
class AuctionID:
    """Value object representing a unique identifier for an auction."""

    value: str

    @classmethod
    def generate(cls) -> "AuctionID":
        return cls(str(uuid.uuid4()))
