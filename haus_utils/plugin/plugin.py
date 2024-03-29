from collections.abc import AsyncGenerator
from typing import Any, Optional
from .types import *


class Plugin:
    def __init__(self, config: PluginConfig, settings: Optional[dict[str, Any]] = None):
        self.config = config
        self.settings = settings

    async def initialize(self):
        pass

    async def close(self):
        pass

    async def get_entities(self, ids: list[str] = None) -> list[PluginEntity]:
        return []

    async def get_actions(self, ids: list[str] = None) -> list[EntityAction]:
        return []

    async def call_action(self, action_id: str, target: str, fields: dict[str, Any]):
        pass

    async def listen_events(self) -> AsyncGenerator[Union[PluginEvent, None]]:
        yield None
