import sqlite3

import pytest

from module.auction.domain.entity import Auction
from module.auction.domain.value_object import AuctionID
from module.auction.infrastructure.sqlite_auction_write_repository import SQLiteAuctionWriteRepository


@pytest.fixture
def db_connection():
    conn = sqlite3.connect(":memory:")
    yield conn
    conn.close()


@pytest.fixture
def repository(db_connection):
    return SQLiteAuctionWriteRepository(db_connection)


def test_save_new_auction(repository):
    auction = Auction(item_id="item-123", starting_price=50.0)
    repository.save(auction)

    assert auction in repository.seen_entities

    # Verify directly in DB
    cursor = repository.connection.cursor()
    cursor.execute("SELECT * FROM auctions WHERE id = ?", (auction.id.value,))
    row = cursor.fetchone()
    assert row is not None
    assert row[0] == auction.id.value
    assert row[1] == "item-123"
    assert row[2] == 50.0
    assert row[3] == 1  # is_active


def test_find_by_id_returns_none_if_missing(repository):
    result = repository.find_by_id(AuctionID("non-existent"))
    assert result is None


def test_find_by_id_returns_auction(repository):
    # Setup
    auction = Auction(item_id="item-123", starting_price=10.0)
    repository.save(auction)

    # Execute
    retrieved = repository.find_by_id(auction.id)

    # Assert
    assert retrieved is not None
    assert retrieved.id == auction.id
    assert retrieved.item_id == auction.item_id
    assert retrieved.starting_price == auction.starting_price
    assert retrieved in repository.seen_entities


def test_save_updates_existing_auction(repository):
    auction = Auction(item_id="item-123", starting_price=10.0)
    repository.save(auction)

    # Modify
    auction.is_active = False
    repository.save(auction)

    # Verify
    retrieved = repository.find_by_id(auction.id)
    assert retrieved.is_active is False


def test_save_persists_bids(repository):
    auction = Auction(item_id="item-123", starting_price=10.0)
    auction.place_bid(bidder_id="bidder-1", amount=15.0)
    auction.place_bid(bidder_id="bidder-2", amount=20.0)

    repository.save(auction)

    retrieved = repository.find_by_id(auction.id)
    assert len(retrieved.bids) == 2
    assert retrieved.bids[0].bidder_id == "bidder-1"
    assert retrieved.bids[0].amount == 15.0
    assert retrieved.bids[1].bidder_id == "bidder-2"
    assert retrieved.bids[1].amount == 20.0
