from typing import Any, Literal, Optional, Union
from pydantic import BaseModel, Field
from secrets import token_urlsafe
from .base import BaseDocument


class ViewServerScope(BaseModel):
    type: Literal["server"]


class ViewUserScope(BaseModel):
    type: Literal["user"]
    owner: str


class ViewPanelPlacement(BaseModel):
    x: int
    y: int
    width: int
    height: int


class Macro(BaseModel):
    id: str = Field(default_factory=lambda: token_urlsafe())
    plugin_id: str
    target: Optional[str] = None
    field_values: Optional[dict[str, Any]] = {}
    icon: str
    tooltip: str


class BaseViewPanel(BaseModel):
    id: str = Field(default_factory=lambda: token_urlsafe())
    type: str
    placement: ViewPanelPlacement
    title: str
    subtitle: Optional[str] = None
    icon: Optional[str] = None


class EntityViewPanel(BaseViewPanel):
    type: Literal["entity"] = "entity"
    plugin_id: str
    entity_id: str
    properties: list[str]
    show_actions: bool
    macros: list[Macro]


class View(BaseDocument):
    name: str
    icon: Optional[str] = None
    scope: Union[ViewServerScope, ViewUserScope]
