# TODO: Move session code
import json
import secrets
from typing import Any, Callable, Coroutine, Generic, Self, TypeVar

from fastapi import Cookie, Response
from pydantic import BaseModel
from redis.asyncio import Redis

from examples.auth.endpoints.exceptions import NOT_AUTHENTICATED


class BaseSessionData(BaseModel):
    user_id: str

DEFAULT_REDIS_SESSION_PREDIX = 'session'
DEFUALT_SESSION_COOKIE_NAME = 'session_id'

SessionData = TypeVar('SessionData', bound=BaseSessionData)


class Session(Generic[SessionData]):
    def __init__(
        self,
        redis_connection: Redis,
        session_id: str,
        session_data_parser: type[SessionData] = BaseSessionData,
        redis_prefix: str = DEFAULT_REDIS_SESSION_PREDIX,
        cookie_name: str = DEFUALT_SESSION_COOKIE_NAME,
    ) -> None:
        super().__init__()

        self.redis = redis_connection

        self._data: SessionData | None = None
        self.data_parser = session_data_parser
        self.session_id = session_id
        self.redis_prefix = redis_prefix
        self.cookie_name = cookie_name


    @staticmethod
    def generate_session_id(nbytes: int = 32) -> str:
        return secrets.token_hex(nbytes)


    @property
    def _redis_key(self) -> str:
        return f'{self.redis_prefix}:{self.session_id}'


    @property
    def data(self) -> SessionData:
        if self._data is None:
            raise ValueError('Session data was None, it should be loaded beforehand')

        return self._data


    async def load(self) -> SessionData | None:
        raw_json = await self.redis.get(self._redis_key)
        if raw_json is None:
            return

        parsed_json = json.loads(raw_json)
        self._data = self.data_parser.parse_obj(parsed_json)

        return self._data


    @classmethod
    async def create_and_load(
        cls,
        redis_connection: Redis,
        session_id: str,
        session_data_parser: type[SessionData],
        redis_prefix: str = 'session',
        cookie_name: str = 'session_id'
    ) -> Self:
        # TODO: Think a more dynamic and better way to do this. This works for now
        session = cls(
            redis_connection,
            session_id,
            session_data_parser,
            redis_prefix,
            cookie_name
        )

        await session.load()
        return session


    # TODO: Implement asymetric encryption for the session_id in a cookie, as far as I am concerned it's called "signed cookies"
    def set_cookie(self, response: Response) -> None:
        response.set_cookie(
            self.cookie_name,
            value=self.session_id,
            secure=False, # TODO: Should be True in production
            httponly=True,
            samesite='lax'
        )


    def delete_cookie(self, response: Response) -> None:
        response.delete_cookie(
            self.cookie_name
        )


    async def destroy(self, response: Response) -> None:
        await self.redis.delete(self._redis_key)
        self.delete_cookie(response)


def current_session(
    redis_instance: Redis,
    session_data_parser: type[SessionData],
    redis_prefix: str = DEFAULT_REDIS_SESSION_PREDIX,
    cookie_name: str = DEFUALT_SESSION_COOKIE_NAME
) -> Callable[..., Coroutine[Any, Any, Session[SessionData]]]:
    async def inner(
        session_id: str | None = Cookie(default=None)
    ) -> Session[SessionData]:
        if session_id is None:
            raise NOT_AUTHENTICATED

        session = await Session.create_and_load(
            redis_instance,
            session_id,
            session_data_parser,
            redis_prefix,
            cookie_name
        )

        return session

    return inner
