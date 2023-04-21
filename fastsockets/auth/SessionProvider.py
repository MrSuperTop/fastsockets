from typing import Callable, Generic

from fastapi import Cookie
from redis.asyncio import Redis

from fastsockets.auth.Session import (
    DEFAULT_REDIS_SESSION_PREDIX,
    DEFUALT_SESSION_COOKIE_NAME,
    Session,
    SessionData,
)
from fastsockets.exceptions import NOT_AUTHENTICATED

# FIXME: Move to a more suitable place
EXAMPLE_SIGN_SECRET = 'example_secret_key'


class SessionProvider(Generic[SessionData]):
    def __init__(
        self,
        session_data_parser: type[SessionData],
        cookie_sign_secret: str,
        redis_provider: Callable[..., Redis],
        redis_prefix: str = DEFAULT_REDIS_SESSION_PREDIX,
        cookie_name: str = DEFUALT_SESSION_COOKIE_NAME
    ) -> None:
        self.redis = redis_provider()
        self.data_parser = session_data_parser
        self.cookie_sign_secret = cookie_sign_secret
        self.redis_prefix = redis_prefix
        self.cookie_name = cookie_name


    async def __call__(
        self,
        session_id: str | None = Cookie(default=None)
    ) -> Session[SessionData]:
        if session_id is None:
            raise NOT_AUTHENTICATED

        loaded_session = await Session.create_and_load(
            self.redis,
            session_id,
            self.data_parser,
            self.cookie_sign_secret,
            self.redis_prefix,
            self.cookie_name
        )

        return loaded_session
