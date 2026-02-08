from __future__ import annotations

import logging
import uuid
from importlib import import_module
from typing import Any

from tripy.core.config import get_settings

logger = logging.getLogger(__name__)


class GraphService:
    def __init__(self) -> None:
        self._graph: Any | None = None

    def _get_graph(self) -> Any:
        if self._graph is not None:
            return self._graph

        settings = get_settings()
        if not settings.graph_enabled:
            raise RuntimeError("Graph workflow is disabled by configuration.")

        module = import_module("graph_chat.finally_graph")
        self._graph = module.graph
        return self._graph

    def execute(
        self,
        *,
        user_input: str,
        thread_id: str | None,
        passenger_id: str,
        interrupt_message: str,
    ) -> tuple[str, str, bool]:
        graph = self._get_graph()

        resolved_thread_id = thread_id or str(uuid.uuid4())
        config = {
            "configurable": {
                "passenger_id": passenger_id,
                "thread_id": resolved_thread_id,
            }
        }

        if user_input.strip().lower() == "y":
            events = graph.stream(None, config, stream_mode="values")
        else:
            events = graph.stream({"messages": ("user", user_input)}, config, stream_mode="values")

        result = ""
        for event in events:
            messages = event.get("messages")
            if not messages:
                continue
            message = messages[-1] if isinstance(messages, list) else messages
            if message.__class__.__name__ == "AIMessage" and getattr(message, "content", None):
                result = message.content

        current_state = graph.get_state(config)
        interrupted = bool(getattr(current_state, "next", None))
        if interrupted:
            result = interrupt_message

        return result, resolved_thread_id, interrupted
