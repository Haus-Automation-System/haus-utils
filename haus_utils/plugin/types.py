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
    settings: dict[str, Union[PluginStringField, PluginNumberField, PluginSwitchField]]

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
    icon: Optional[str] = None


class BaseActionField(BaseModel):
    key: str
    display: DisplayData


class StringActionField(BaseActionField):
    type: Literal["string"]


class NumberActionField(BaseActionField):
    type: Literal["number"]
    decimals: Optional[bool] = True
    min: Optional[Union[int, float]] = None
    max: Optional[Union[int, float]] = None


class BooleanActionField(BaseActionField):
    type: Literal["boolean"]


class SelectionActionOptions(BaseModel):
    value: str
    label: Optional[str]
    disabled: Optional[bool] = False


class SelectionActionField(BaseActionField):
    type: Literal["selection"]
    options: list[SelectionActionOptions]
    multi: Optional[bool] = False


class DateActionField(BaseActionField):
    type: Literal["date"]
    min: datetime.datetime
    max: datetime.datetime


class ColorActionField(BaseActionField):
    type: Literal["color"]
    alpha: Optional[bool] = False


ENTITY_ACTION_FIELDS = Union[
    StringActionField,
    NumberActionField,
    BooleanActionField,
    SelectionActionField,
    DateActionField,
    ColorActionField,
]


class EntityAction(BaseModel):
    id: str
    plugin: str
    display: DisplayData
    target_types: list[str]
    fields: list[ENTITY_ACTION_FIELDS]


class BaseEntityProperty(BaseModel):
    id: str
    type: str
    display: DisplayData
    value: Any


class StringEntityProperty(BaseEntityProperty):
    type: Literal["string"]
    value: Optional[str] = ""


class NumberEntityProperty(BaseEntityProperty):
    type: Literal["number"]
    value: Optional[Union[int, float]] = 0


class BooleanEntityProperty(BaseEntityProperty):
    type: Literal["boolean"]
    value: Optional[bool] = False


class ListEntityProperty(BaseEntityProperty):
    type: Literal["list"]
    value: Optional[list] = Field(default_factory=list)


class TablePropertyColumn(BaseEntityProperty):
    key: str
    value_type: Literal["string", "number", "boolean", "list"]


class TableEntityProperty(BaseEntityProperty):
    type: Literal["table"]
    columns: list[TablePropertyColumn]
    value: list[dict[str, Any]]


class DateEntityProperty(BaseEntityProperty):
    type: Literal["date"]
    value: datetime.datetime


class ColorEntityProperty(BaseEntityProperty):
    type: Literal["color"]
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
