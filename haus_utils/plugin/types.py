from io import FileIO
from typing import Literal, Optional
from pydantic import BaseModel
import yaml


class PluginPypiDepenency(BaseModel):
    mode: Literal["pypi"]
    name: str
    version: Optional[str]
    extras: Optional[list[str]]


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
        )
