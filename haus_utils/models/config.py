from pydantic import BaseModel
from yaml import load, Loader


class ServerDatabaseConfig(BaseModel):
    uri: str
    database: str


class ServerSecuritySessionsConfig(BaseModel):
    expiration: float


class ServerSecurityAccessLevelsConfig(BaseModel):
    internal: list[str]
    privileged: list[str]
    external: list[str]


class ServerSecurityUsersDefaultConfig(BaseModel):
    username: str
    password: str
    create_if_not_present: bool


class ServerSecurityUsersConfig(BaseModel):
    default: ServerSecurityUsersDefaultConfig


class ServerSecurityConfig(BaseModel):
    sessions: ServerSecuritySessionsConfig
    access_levels: ServerSecurityAccessLevelsConfig
    users: ServerSecurityUsersConfig


class ServerConfig(BaseModel):
    database: ServerDatabaseConfig
    security: ServerSecurityConfig


class Config(BaseModel):
    server: ServerConfig

    @classmethod
    def from_config(cls, path: str) -> "Config":
        with open(path, "r") as f:
            return Config(**load(f.read(), Loader))
