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
