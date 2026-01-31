import os
import sqlite3
import tempfile

import pytest

from module.auction.domain.entity import Auction
from module.auction.infrastructure.sqlite_auction_read_repository import SQLiteAuctionReadRepository
from module.auction.infrastructure.sqlite_auction_write_repository import SQLiteAuctionWriteRepository


@pytest.fixture
def temp_db_path():
    fd, path = tempfile.mkstemp()
    os.close(fd)
    yield path
    os.remove(path)


@pytest.fixture
def populated_db_path(temp_db_path):
    conn = sqlite3.connect(temp_db_path)
    write_repo = SQLiteAuctionWriteRepository(conn)

    # Create some test data
    a1 = Auction("item-1", 10.0)
    a1.place_bid("u1", 15.0)

    a2 = Auction("item-2", 20.0)
    a2.is_active = False

    write_repo.save(a1)
    write_repo.save(a2)
    conn.commit()
    conn.close()

    return temp_db_path, a1, a2


def test_list_auctions(populated_db_path):
    db_path, a1, a2 = populated_db_path
    repo = SQLiteAuctionReadRepository(db_path)

    auctions = repo.list_auctions()
    assert len(auctions) == 2

    # Verify minimal DTO fields
    ids = {a["id"] for a in auctions}
    assert a1.id.value in ids
    assert a2.id.value in ids


def test_get_auction(populated_db_path):
    db_path, a1, a2 = populated_db_path
    repo = SQLiteAuctionReadRepository(db_path)

    # Test valid fetch
    data = repo.get_auction(a1.id.value)
    assert data is not None
    assert data["id"] == a1.id.value
    assert data["item_id"] == "item-1"
    assert data["starting_price"] == 10.0
    assert data["is_active"] is True
    assert len(data["bids"]) == 1
    assert data["bids"][0]["bidder_id"] == "u1"

    # Test not found
    assert repo.get_auction("missing") is None


def test_list_bids(populated_db_path):
    db_path, a1, a2 = populated_db_path
    repo = SQLiteAuctionReadRepository(db_path)

    bids = repo.list_bids(a1.id.value)
    assert len(bids) == 1
    assert bids[0]["bidder_id"] == "u1"
    assert bids[0]["amount"] == 15.0

    assert repo.list_bids("missing") is None
