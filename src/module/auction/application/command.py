from dataclasses import dataclass

from shared.application.command import Command


@dataclass
class PlaceBidCommand(Command):
    """Command to place a bid on an auction."""

    auction_id: str
    bidder_id: str
    amount: float


@dataclass
class CreateAuctionCommand(Command):
    """Command to create a new auction."""

    item_id: str
    starting_price: float
