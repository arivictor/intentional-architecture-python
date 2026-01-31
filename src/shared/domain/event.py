from dataclasses import dataclass


@dataclass(frozen=True)
class Event:
    """Base class for domain events."""

    pass
