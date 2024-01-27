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


class ViewParent(BaseModel):
    type: Literal["view", "panel"]
    id: str


class BaseViewPanel(BaseDocument):
    id: str = Field(default_factory=lambda: token_urlsafe())
    parent: ViewParent
    type: str
    placement: ViewPanelPlacement
    title: str
    subtitle: Optional[str] = None
    icon: Optional[str] = None

    class Settings:
        name = "panels"
        is_root = True


class EntityViewPanel(BaseViewPanel):
    type: Literal["entity"] = "entity"
    plugin_id: str
    entity_id: str
    properties: list[str]
    show_actions: bool
    macros: list[Macro]


class BaseView(BaseDocument):
    type: str
    name: str
    icon: Optional[str] = None
    scope: Union[ViewServerScope, ViewUserScope]

    class Settings:
        name = "views"
        is_root = True


class PanelledView(BaseView):
    type: Literal["panelled"] = "panelled"


class MapViewStateFilterAttributes(BaseModel):
    attribute: str
    value: Any
    operation: Literal["eq", "ne", "gt", "lt", "ge", "le"]


class MapViewStateFilter(BaseModel):
    attributes: list[MapViewStateFilterAttributes]
    union: Literal["all", "any", "one", "none"]


class MapViewInteractableState(BaseModel):
    filters: list[MapViewStateFilter]
    state: str
    state_description: str
    icon: str


class EntityIdentifier(BaseModel):
    plugin: str
    entity_id: str


class MapViewInteractable(BaseModel):
    id: str = Field(default_factory=lambda: token_urlsafe())
    position_x: float
    position_y: float
    name: str
    default_icon: str
    entity: EntityIdentifier
    states: list[MapViewInteractableState]
    action: Macro


class MapView(BaseView):
    type: Literal["map"] = "map"
    image: str
    interactables: list[MapViewInteractable]
