from dataclasses import dataclass, field
from datetime import UTC, datetime

from shared.domain.event import Event


@dataclass(frozen=True)
class BidPlaced(Event):
    """Event triggered when a bid is successfully placed."""

    auction_id: str
    bidder_id: str
    amount: float
    occurred_at: str = field(default_factory=lambda: str(datetime.now(UTC)))
