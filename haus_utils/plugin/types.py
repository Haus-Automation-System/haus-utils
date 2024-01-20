import datetime
from email.policy import default
from io import FileIO
from typing import Any, Literal, Optional, Union
from pydantic import BaseModel, Field
import yaml


class PluginPypiDepenency(BaseModel):
    mode: Literal["pypi"]
    name: str
    version: Optional[str]
    extras: Optional[list[str]]


class PluginField(BaseModel):
    name: str
    icon: Optional[str] = None
    required: Optional[bool] = False
    placeholder: Optional[str] = Field(default_factory=str)


class PluginStringField(PluginField):
    type: Literal["string"]
    default: Optional[str] = Field(default_factory=str)


class PluginNumberField(PluginField):
    type: Literal["number"]
    default: Optional[Union[int, float]] = 0
    min: Optional[Union[int, float]] = None
    max: Optional[Union[int, float]] = None


class PluginSwitchField(PluginField):
    type: Literal["switch"]
    default: Optional[bool] = None


class PluginMetadata(BaseModel):
    name: str
    version: str
    icon: str
    display_name: str


class PluginRun(BaseModel):
    module: str
    entrypoint: str
    dependencies: dict[str, PluginPypiDepenency]


class PluginConfig(BaseModel):
    metadata: PluginMetadata
    run: PluginRun
    settings: dict[str, Union[PluginStringField,
                              PluginNumberField, PluginSwitchField]]

    @classmethod
    def from_manifest(cls, fd: FileIO) -> "PluginConfig":
        raw = yaml.load(fd.read(), yaml.Loader)
        meta = raw["metadata"]
        run = raw["run"]

        deps = {}
        for k, v in run["dependencies"].items():
            match v["mode"]:
                case "pypi":
                    deps[k] = PluginPypiDepenency(
                        mode="pypi",
                        name=v["package"],
                        version=v.get("version"),
                        extras=v.get("extras"),
                    )

        sets = {}
        for k, v in raw["settings"].items():
            match v["type"]:
                case "string":
                    sets[k] = PluginStringField(**v)
                case "number":
                    sets[k] = PluginNumberField(**v)
                case "switch":
                    sets[k] = PluginSwitchField(**v)

        return PluginConfig(
            metadata=PluginMetadata(
                name=meta["name"],
                version=meta["version"],
                icon=meta["icon"],
                display_name=meta["display-name"],
            ),
            run=PluginRun(
                module=run["module"], entrypoint=run["entrypoint"], dependencies=deps
            ),
            settings=sets,
        )


class DisplayData(BaseModel):
    label: str
    sub_label: Optional[str] = None
    icon: Optional[str] = None


class BaseActionField(BaseModel):
    key: str
    display: DisplayData
    advanced: bool
    default: Any
    required: bool
    example: Optional[Any]


class StringActionField(BaseActionField):
    type: Literal["string"] = "string"


class NumberActionField(BaseActionField):
    type: Literal["number"] = "number"
    decimals: Optional[bool] = True
    min: Optional[Union[int, float]] = None
    max: Optional[Union[int, float]] = None
    unit: Optional[str] = None


class BooleanActionField(BaseActionField):
    type: Literal["boolean"] = "boolean"


class SelectionActionOptions(BaseModel):
    value: str
    label: Optional[str]
    disabled: Optional[bool] = False


class SelectionActionField(BaseActionField):
    type: Literal["selection"] = "selection"
    options: list[SelectionActionOptions]
    multi: Optional[bool] = False


class DateActionField(BaseActionField):
    type: Literal["date"] = "date"
    min: Optional[datetime.date]
    max: Optional[datetime.date]


class TimeActionField(BaseActionField):
    type: Literal["time"] = "time"
    min: Optional[datetime.time]
    max: Optional[datetime.time]


class DateTimeActionField(BaseActionField):
    type: Literal["datetime"] = "datetime"
    min: Optional[datetime.datetime]
    max: Optional[datetime.datetime]


class ColorActionField(BaseActionField):
    type: Literal["color"] = "color"
    alpha: Optional[bool] = False


class EntitySelectorActionField(BaseActionField):
    type: Literal["entity"] = "entity"
    prefix: list[str]


class JSONActionField(BaseActionField):
    type: Literal["json"] = "json"


ENTITY_ACTION_FIELDS = Union[
    StringActionField,
    NumberActionField,
    BooleanActionField,
    SelectionActionField,
    DateActionField,
    TimeActionField,
    DateTimeActionField,
    ColorActionField,
    EntitySelectorActionField,
    JSONActionField
]


class EntityAction(BaseModel):
    id: str
    plugin: str
    category: str
    display: DisplayData
    target_types: Union[list[str], None]
    fields: dict[str, ENTITY_ACTION_FIELDS]


class BaseEntityProperty(BaseModel):
    id: str
    type: str
    display: DisplayData
    value: Any


class StringEntityProperty(BaseEntityProperty):
    type: Literal["string"] = "string"
    value: Optional[str] = ""


class NumberEntityProperty(BaseEntityProperty):
    type: Literal["number"] = "number"
    value: Optional[Union[int, float]] = 0


class BooleanEntityProperty(BaseEntityProperty):
    type: Literal["boolean"] = "boolean"
    value: Optional[bool] = False


class ListEntityProperty(BaseEntityProperty):
    type: Literal["list"] = "list"
    value: Optional[list] = Field(default_factory=list)


class TablePropertyColumn(BaseModel):
    key: str
    value_type: str


class TableEntityProperty(BaseEntityProperty):
    type: Literal["table"] = "table"
    columns: list[TablePropertyColumn]
    value: list[dict[str, Any]]


class DateEntityProperty(BaseEntityProperty):
    type: Literal["date"] = "date"
    value: datetime.datetime


class ColorEntityProperty(BaseEntityProperty):
    type: Literal["color"] = "color"
    hasAlpha: Optional[bool] = False
    value: str


ENTITY_PROPERTIES = Union[
    StringEntityProperty,
    NumberEntityProperty,
    BooleanEntityProperty,
    ListEntityProperty,
    TableEntityProperty,
    DateEntityProperty,
    ColorEntityProperty,
]


class PluginEntity(BaseModel):
    id: str
    plugin: str
    type: str
    display: DisplayData
    properties: dict[str, ENTITY_PROPERTIES]


class PluginEvent(BaseModel):
    id: str
    plugin: str
    types: list[str]
    data: Any
    targets: list[str]
    new_state: Optional[PluginEntity] = None
