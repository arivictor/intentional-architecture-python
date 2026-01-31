from typing import Any, Protocol


class AuctionReadRepository(Protocol):
    """
    Interface for the Read Model (Query Side).
    Acts as a repository for retrieving Read DTOs.
    """

    def list_auctions(self) -> list[dict[str, Any]]: ...

    def get_auction(self, auction_id: str) -> dict[str, Any] | None: ...

    def list_bids(self, auction_id: str) -> list[dict[str, Any]] | None: ...
