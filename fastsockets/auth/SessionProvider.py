from typing import Generic

from fastapi import Cookie, Depends
from redis.asyncio import Redis

from examples.auth.endpoints.exceptions import NOT_AUTHENTICATED
from examples.auth.get_redis import get_redis
from fastsockets.auth.Session import (
    DEFAULT_REDIS_SESSION_PREDIX,
    DEFUALT_SESSION_COOKIE_NAME,
    Session,
    SessionData,
)

# FIXME: Move me in a more suitable place
EXAMPLE_SIGN_SECRET = 'example_secret_key'


class SessionProvider(Generic[SessionData]):
    def __init__(
        self,
        session_data_parser: type[SessionData],
        cookie_sign_secret: str,
        redis_prefix: str = DEFAULT_REDIS_SESSION_PREDIX,
        cookie_name: str = DEFUALT_SESSION_COOKIE_NAME
    ) -> None:
        self.data_parser = session_data_parser
        self.cookie_sign_secret = cookie_sign_secret
        self.redis_prefix = redis_prefix
        self.cookie_name = cookie_name


    async def __call__(
        self,
        redis: Redis = Depends(get_redis),
        session_id: str = Cookie()
    ) -> Session[SessionData]:
        if session_id is None:
            raise NOT_AUTHENTICATED

        loaded_session = await Session.create_and_load(
            redis,
            session_id,
            self.data_parser,
            self.cookie_sign_secret,
            self.redis_prefix,
            self.cookie_name
        )

        return loaded_session
