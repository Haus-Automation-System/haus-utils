from typing import Literal, Optional, Union

from pydantic import BaseModel
from .base import BaseDocument, ExpirableDocument
from hashlib import pbkdf2_hmac
from os import urandom


class Session(ExpirableDocument):
    user_id: Optional[str]

    @classmethod
    def create(cls, expire: float) -> "Session":
        return Session(user_id=None, expire_at=cls.expire_time(expire))

    class Settings:
        name = "sessions"


class RedactedUser(BaseModel):
    id: str
    username: str
    display_name: Optional[str]
    user_icon: Optional[str]
    scopes: list[str]


class User(BaseDocument):
    username: str
    display_name: Optional[str] = None
    password_hash: str
    password_salt: str
    user_icon: Optional[str] = None
    scopes: list[Union[Literal["root"], str]] = []

    class Settings:
        name = "users"

    @classmethod
    def create(cls, username: str, password: str) -> "User":
        salt = urandom(32)
        key = pbkdf2_hmac("sha256", password.encode(), salt, 500000)
        return User(
            username=username,
            password_hash=key.hex(),
            password_salt=salt.hex(),
            scopes=[],
        )

    def verify(self, password: str) -> bool:
        salt = bytes.fromhex(self.password_salt)
        key = pbkdf2_hmac("sha256", password.encode(), salt, 500000).hex()
        return key == self.password_hash

    def has_scope(self, scope: str) -> bool:
        if "root" in self.scopes:
            return True

        check = scope
        while len(check) > 0:
            if check in self.scopes:
                return True
            scope = ".".join(scope.split(".")[:-1])

        return False

    @property
    def redacted(self) -> RedactedUser:
        return RedactedUser(
            id=self.id,
            username=self.username,
            display_name=self.display_name,
            user_icon=self.user_icon,
            scopes=self.scopes,
        )
