from datetime import datetime, timedelta
from beanie import Document, Indexed
from pydantic import Field
from secrets import token_urlsafe


class BaseDocument(Document):
    id: str = Field(default_factory=lambda: token_urlsafe(32))


class ExpirableDocument(BaseDocument):
    expire_at: Indexed(datetime, expireAfterSeconds=0)

    async def renew(self, seconds: float):
        self.expire_at = datetime.utcnow() + timedelta(seconds=seconds)
        await self.save()

    @classmethod
    def expire_time(self, seconds: float) -> datetime:
        return datetime.utcnow() + timedelta(seconds=seconds)

    class Settings:
        name = "sessions"
