from module.auction.application.event_handler import send_email_to_bidder, update_analytics
from module.auction.application.query import GetAuctionQuery, ListAuctionsQuery, ListBidsQuery
from module.auction.application.query_handler import (
    GetAuctionHandler,
    ListAuctionsHandler,
    ListBidsHandler,
)
from module.auction.domain.event import BidPlaced
from module.auction.infrastructure.sqlite_auction_read_repository import SQLiteAuctionReadRepository
from shared.application.command_bus import CommandBus
from shared.application.event_bus import EventBus
from shared.application.query_bus import QueryBus


def bootstrap_dependencies(db_path: str = "auctions.db") -> tuple[EventBus, CommandBus, QueryBus]:
    """
    Sets up the dependency injection container and wires the application.
    Returns the event, command, and query buses ready for use.
    """
    event_bus = EventBus()
    command_bus = CommandBus()
    query_bus = QueryBus()

    # INFRASTRUCTURE
    # Read Repo (Read Side) - Singleton-ish (stateless)
    read_repo = SQLiteAuctionReadRepository(db_path)

    # Wiring: Register Event Listeners
    event_bus.subscribe(BidPlaced, send_email_to_bidder)
    event_bus.subscribe(BidPlaced, update_analytics)

    # Wiring: Register Query Handlers
    query_bus.register(GetAuctionQuery, GetAuctionHandler(read_repo))
    query_bus.register(ListAuctionsQuery, ListAuctionsHandler(read_repo))
    query_bus.register(ListBidsQuery, ListBidsHandler(read_repo))

    # Wiring: Register Command Handlers
    # Note: UoW is created per-request inside the actual execution flow (main.py),
    # so we don't register instances here for commands yet in this simple example.

    return event_bus, command_bus, query_bus
