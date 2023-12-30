from typing import Any, Optional
from .types import *


class Plugin:
    def __init__(self, config: PluginConfig, settings: Optional[dict[str, Any]] = None):
        self.config = config
        self.settings = settings
