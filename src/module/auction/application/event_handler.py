import logging

from module.auction.domain.event import BidPlaced

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def send_email_to_bidder(event: BidPlaced):
    """
    Simulates sending an email to the bidder.
    In a real system, this would trigger an email service provider API.
    """
    logger.info(f"📧 EMAIL: Hello user {event.bidder_id}, your bid of ${event.amount} was accepted!")


def update_analytics(event: BidPlaced):
    """
    Simulates updating an analytics dashboard.
    In a real system, this might push data to a data warehouse or queue.
    """
    logger.info(f"📊 ANALYTICS: Auction {event.auction_id} received a new bid.")
