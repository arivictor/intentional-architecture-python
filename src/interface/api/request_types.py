from collections.abc import Callable
from typing import Any

# Type alias for request/response logic
# Request -> (Status, Data)
ControllerFunc = Callable[[dict[str, Any] | None, dict[str, str]], tuple[int, Any]]
