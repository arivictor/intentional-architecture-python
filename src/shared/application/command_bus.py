from typing import Any

from shared.application.command import Command


class CommandBus:
    """In-memory command bus for dispatching commands to their handlers."""

    def __init__(self):
        self._handlers: dict[type[Command], Any] = {}

    def register(self, cmd_type: type[Command], handler: Any):
        self._handlers[cmd_type] = handler

    def dispatch(self, cmd: Command):
        self._handlers[type(cmd)].handle(cmd)
