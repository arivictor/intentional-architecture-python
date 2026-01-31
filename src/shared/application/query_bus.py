from typing import Any

from shared.application.query import Query


class QueryBus:
    """In-memory query bus for dispatching queries to their handlers."""

    def __init__(self):
        self._handlers: dict[type[Query], Any] = {}

    def register(self, query_type: type[Query], handler: Any):
        self._handlers[query_type] = handler

    def dispatch(self, query: Query) -> Any:
        handler = self._handlers.get(type(query))
        if not handler:
            raise Exception(f"No handler registered for {type(query)}")
        return handler.handle(query)
