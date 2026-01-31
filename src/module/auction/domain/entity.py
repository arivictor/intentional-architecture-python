from module.auction.domain.event import BidPlaced
from module.auction.domain.exception import AuctionException
from module.auction.domain.value_object import AuctionID, Bid
from shared.domain.event import Event


class Auction:
    """Aggregate root representing an auction."""

    def __init__(self, item_id: str, starting_price: float):
        self.id = AuctionID.generate()
        self.item_id = item_id
        self.starting_price = starting_price
        self.bids: list[Bid] = []
        self.is_active = True
        self.events: list[Event] = []

    @property
    def current_price(self) -> float:
        """Get the current highest bid or starting price if no bids."""
        if not self.bids:
            return self.starting_price
        return self.bids[-1].amount

    def place_bid(self, bidder_id: str, amount: float):
        """Place a bid on the auction."""
        if not self.is_active:
            raise AuctionException("Auction is closed.")
        if amount <= self.current_price:
            raise AuctionException(f"Bid of {amount} must be higher than current price {self.current_price}")

        # State Change
        new_bid = Bid(bidder_id, amount)
        self.bids.append(new_bid)

        # Event: Record that this happened
        self.events.append(BidPlaced(auction_id=self.id.value, bidder_id=bidder_id, amount=amount))
