from dataclasses import dataclass

from shared.application.query import Query


@dataclass
class GetAuctionQuery(Query):
    auction_id: str


@dataclass
class ListAuctionsQuery(Query):
    pass


@dataclass
class ListBidsQuery(Query):
    auction_id: str
