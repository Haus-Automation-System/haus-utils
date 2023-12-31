from email.policy import default
from io import FileIO
from typing import Literal, Optional, Union
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
