from typing import Any

from module.auction.application.query import GetAuctionQuery, ListAuctionsQuery, ListBidsQuery
from module.auction.application.read_repository import AuctionReadRepository


class GetAuctionHandler:
    def __init__(self, repo: AuctionReadRepository):
        self.repo = repo

    def handle(self, query: GetAuctionQuery) -> dict[str, Any] | None:
        return self.repo.get_auction(query.auction_id)


class ListAuctionsHandler:
    def __init__(self, repo: AuctionReadRepository):
        self.repo = repo

    def handle(self, query: ListAuctionsQuery) -> list[dict[str, Any]]:
        return self.repo.list_auctions()


class ListBidsHandler:
    def __init__(self, repo: AuctionReadRepository):
        self.repo = repo

    def handle(self, query: ListBidsQuery) -> list[dict[str, Any]] | None:
        return self.repo.list_bids(query.auction_id)
