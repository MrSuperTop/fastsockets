import json
import secrets
from typing import Any, Callable, Generic, Self, TypeVar

from fastapi import Response
from itsdangerous import BadSignature, Serializer, URLSafeSerializer
from pydantic import BaseModel
from redis.asyncio import Redis

from fastsockets.exceptions import NOT_AUTHENTICATED


class BaseSessionData(BaseModel):
    user_id: int


DEFAULT_REDIS_SESSION_PREDIX = 'session'
DEFUALT_SESSION_COOKIE_NAME = 'session_id'
DEFAULT_SESSION_ID_LENGHT = 32

SessionData = TypeVar('SessionData', bound=BaseSessionData)


class Session(Generic[SessionData]):
    # TODO: Create more extensible API for passing CookieSerializer and other stuff
    def __init__(
        self,
        redis_connection: Redis,
        session_id: str,
        session_data_parser: type[SessionData],
        cookie_sign_key: str,
        redis_prefix: str = DEFAULT_REDIS_SESSION_PREDIX,
        cookie_name: str = DEFUALT_SESSION_COOKIE_NAME,
    ) -> None:
        super().__init__()

        serializer_provider = Session.get_cookie_serializer(cookie_sign_key)
        serializer = serializer_provider()

        self.redis = redis_connection
        self.serializer = serializer

        self._data: SessionData | None = None
        self.data_parser = session_data_parser
        self.session_id = session_id
        self.redis_prefix = redis_prefix
        self.cookie_name = cookie_name

    def _parse_data(self, raw_json: Any) -> SessionData | None:
        if self._data is None:
            return

        return self.data_parser.parse_obj(raw_json)

    @staticmethod
    def get_cookie_serializer(
            secret_key: str
    ) -> Callable[..., Serializer]:
        def inner() -> Serializer:
            serializer = URLSafeSerializer(
                secret_key
            )

            return serializer

        return inner

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

    @data.setter
    def data(self, new_value: SessionData):
        self._data = new_value

    async def load(self) -> SessionData | None:
        raw_json = await self.redis.get(self._redis_key)
        if raw_json is None:
            return

        parsed_json = json.loads(raw_json)
        if self.data_parser is None:
            return

        self._data = self.data_parser.parse_obj(parsed_json)

        return self._data

    @classmethod
    async def create_and_load(
        cls,
        redis_connection: Redis,
        signed_session_id: str,
        session_data_parser: type[SessionData],
        cookie_sign_key: str,
        redis_prefix: str = 'session',
        cookie_name: str = 'session_id'
    ) -> Self:
        # TODO: Think a more dynamic and better way to do this. This works for now
        serializer_provider = Session.get_cookie_serializer(cookie_sign_key)
        serializer = serializer_provider()

        try:
            session_id = serializer.loads(signed_session_id)
        except BadSignature:
            raise NOT_AUTHENTICATED

        session = cls(
            redis_connection,
            session_id,
            session_data_parser,
            cookie_sign_key,
            redis_prefix,
            cookie_name
        )


        await session.load()

        return session

    @classmethod
    async def create_and_save(
            cls,
            redis_connection: Redis,
            session_data: SessionData,
            cookie_sign_key: str,
            redis_prefix: str = 'session',
            cookie_name: str = 'session_id'
    ) -> Self:
        session_id = Session.generate_session_id()

        session = cls(
            redis_connection,
            session_id,
            session_data.__class__,
            cookie_sign_key,
            redis_prefix,
            cookie_name
        )

        session.data = session_data
        await session.save()

        return session


    async def save(self):
        if self._data is None:
            return

        raw_data = self._data.json()
        await self.redis.set(self._redis_key, raw_data)

    def set_cookie(self, response: Response) -> None:
        cookie_value = self.serializer.dumps(self.session_id)
        if not isinstance(cookie_value, str):
            return

        response.set_cookie(
            self.cookie_name,
            value=cookie_value,
            secure=False,  # TODO: Should be True in production, provide a way to configure this
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
