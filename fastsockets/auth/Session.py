# TODO: Move session code
import json
import pickle
import secrets
from typing import Any, Callable, Coroutine, Generic, Self, TypeVar

from fastapi import Cookie, Depends, Response
from pydantic import BaseModel
from redis.asyncio import Redis
import redis
from examples.auth.endpoints.exceptions import NOT_AUTHENTICATED
from examples.auth.get_redis import get_redis
from examples.auth.db.models.User import User


class BaseSessionData(BaseModel):
    user_id: str

DEFAULT_REDIS_SESSION_PREDIX = 'session'
DEFUALT_SESSION_COOKIE_NAME = 'session_id'

SessionData = TypeVar('SessionData', bound=BaseSessionData)


class Session(Generic[SessionData]):
    redis = None

    def __init__(
        self,
        # redis_connection: Redis,
        session_id: str,
        user: User,
        session_data_parser: type[SessionData] = BaseSessionData,
        redis_prefix: str = DEFAULT_REDIS_SESSION_PREDIX,
        cookie_name: str = DEFUALT_SESSION_COOKIE_NAME,
    ) -> None:
        super().__init__()

        # self.redis = redis_connection

        self._data: SessionData | None = None
        self.data_parser = session_data_parser
        self.session_id = session_id
        self.redis_prefix = redis_prefix
        self.cookie_name = cookie_name
        self.user = user


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
        # redis_connection: Redis,
        session_id: str,
        session_data_parser: type[SessionData],
        user: User,
        redis_prefix: str = 'session',
        cookie_name: str = 'session_id'
    ) -> Self:
        # TODO: Think a more dynamic and better way to do this. This works for now
        session = cls(
            # redis_connection,
            session_id,
            user,
            session_data_parser,
            redis_prefix,
            cookie_name
        )
        session._data = session_id

        await cls.redis.set(session_id, pickle.dumps(session))
        await cls.redis.sadd(str(user.id), pickle.dumps(session))

        return session


    async def save(self):
        if self._data is None:
            return


        raw_data = self._data.json()
        await self.redis.set(self._redis_key, raw_data)


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


async def get_current_session_by_cookie(session_id: str = Cookie(default=None)) -> Session[SessionData]:
    try:
        session = await Session.redis.get(session_id)
    except redis.exceptions.DataError:
        raise NOT_AUTHENTICATED

    if session is None:
        # TODO implement errors in websocket
        raise NOT_AUTHENTICATED

    session = pickle.loads(session)
    return session


# def current_session(
#     session_data_parser: type[SessionData],
#     redis_prefix: str = DEFAULT_REDIS_SESSION_PREDIX,
#     cookie_name: str = DEFUALT_SESSION_COOKIE_NAME
# ) -> Callable[..., Coroutine[Any, Any, Session[SessionData]]]:
#     async def inner(
#         redis: Redis = Depends(get_redis),
#         session: Session[SessionData] = Depends(get_current_session_by_cookie)
#
#     ) -> Session[SessionData]:
#         if session is None:
#             raise NOT_AUTHENTICATED
#
#         # session = await Session.create_and_load(
#         #     session_id,
#         #     session_data_parser,
#         #     # user,
#         #     redis_prefix,
#         #     cookie_name
#         # )
#
#         return session
#
#     return inner
