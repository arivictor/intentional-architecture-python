import os
import sqlite3
import tempfile
from unittest.mock import Mock

import pytest

from module.auction.domain.entity import Auction, BidPlaced
from module.auction.infrastructure.sqlite_auction_unit_of_work import SQLiteAuctionUnitOfWork
from shared.application.event_bus import EventBus


@pytest.fixture
def temp_db_path():
    fd, path = tempfile.mkstemp()
    os.close(fd)
    yield path
    os.remove(path)


def test_uow_manages_connection(temp_db_path):
    event_bus = Mock(spec=EventBus)
    uow = SQLiteAuctionUnitOfWork(event_bus, temp_db_path)

    assert uow.connection is None

    with uow:
        assert uow.connection is not None
        assert isinstance(uow.connection, sqlite3.Connection)
        assert uow.repo is not None

    # Should be closed after exit (but the object reference might remain,
    # sqlite3 objects don't always clear the var, but we can check if it's usable or use mocks)
    # The __exit__ calls close on the connection.
    # We can verify by trying to use it, expecting ProgrammingError
    with pytest.raises(sqlite3.ProgrammingError):
        uow.connection.execute("SELECT 1")


def test_uow_commit_publishes_events(temp_db_path):
    event_bus = Mock(spec=EventBus)
    uow = SQLiteAuctionUnitOfWork(event_bus, temp_db_path)

    with uow:
        auction = Auction("item-1", 10.0)
        auction.place_bid("u1", 15.0)
        # This adds an event to auction.events

        uow.repo.save(auction)

        # At this point events are on the entity, but not published
        event_bus.publish.assert_not_called()

    # After exit (auto-commit)
    assert event_bus.publish.called
    # Check if the right event was passed.
    # Note: uow calls publish with a list of events
    args = event_bus.publish.call_args[0][0]  # first arg, which is the list
    assert len(args) == 1
    assert isinstance(args[0], BidPlaced)


def test_uow_rollback_on_error(temp_db_path):
    event_bus = Mock(spec=EventBus)
    uow = SQLiteAuctionUnitOfWork(event_bus, temp_db_path)

    try:
        with uow:
            auction = Auction("item-1", 10.0)
            uow.repo.save(auction)
            raise ValueError("Something went wrong")
    except ValueError:
        pass

    # Verify not persisted
    conn = sqlite3.connect(temp_db_path)
    cursor = conn.cursor()
    # Table might exist depending on implementation, but row shouldn't
    try:
        cursor.execute("SELECT * FROM auctions")
        rows = cursor.fetchall()
        assert len(rows) == 0
    except sqlite3.OperationalError:
        # If table wasn't created/committed, this is also fine
        pass
    finally:
        conn.close()

    # Verify no events published
    event_bus.publish.assert_not_called()
