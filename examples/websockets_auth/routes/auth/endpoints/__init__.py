from argon2.exceptions import VerificationError
from fastapi import APIRouter, Depends, Response
from redis.asyncio import Redis

from examples.websockets_auth.db import get_user, get_user_by_id, users_db
from examples.websockets_auth.db.models.User import User
from examples.websockets_auth.dependencies.not_authenticated import not_authenticated
from examples.websockets_auth.get_redis import get_redis
from examples.websockets_auth.hasher import ph
from examples.websockets_auth.routes.auth.exceptions import (
    INVALID_USER_CREDENTIALS,
    USER_ALREADY_EXISTS,
    USER_NOT_FOUND,
)
from examples.websockets_auth.routes.auth.inputs.login import (
    LoginInput,
    LoginResponse,
    PublicUser,
)
from examples.websockets_auth.routes.auth.inputs.logout import LogoutResponse
from examples.websockets_auth.routes.auth.inputs.register import (
    RegisterInput,
    RegisterResponse,
)
from examples.websockets_auth.session import SessionData, session_provider
from fastsockets.auth.Session import Session
from fastsockets.auth.SessionProvider import EXAMPLE_SIGN_SECRET

router = APIRouter()

@router.post('/login', dependencies=[Depends(not_authenticated)])
async def login(
    credentials: LoginInput,
    response: Response,
    redis: Redis = Depends(get_redis)
) -> LoginResponse:
    user_predicate = await get_user(credentials.usernameOrEmail)
    if user_predicate is None:
        raise INVALID_USER_CREDENTIALS

    try:
        ph.verify(user_predicate.password, credentials.password)
    except VerificationError:
        raise INVALID_USER_CREDENTIALS

    session_data = SessionData(
        user_id=user_predicate.id
    )

    session = await Session.create_and_save(
        redis,
        session_data,
        EXAMPLE_SIGN_SECRET
    )

    session.set_cookie(response)

    return LoginResponse(
        user=PublicUser.parse_obj(user_predicate)
    )


@router.post('/register', dependencies=[Depends(not_authenticated)])
async def register(
    data: RegisterInput,
    response: Response,
    redis: Redis = Depends(get_redis)
) -> RegisterResponse:
    user_exists = any([await get_user(data.username), await get_user(data.email)])
    if user_exists:
        raise USER_ALREADY_EXISTS

    new_user = User.parse_obj({
        "id": users_db[-1].id + 1,
        **data.dict()
    })

    users_db.append(new_user)

    session_data = SessionData(
        user_id=new_user.id
    )

    # FIXME
    new_session = await Session.create_and_save(
        redis,
        session_data,
        EXAMPLE_SIGN_SECRET
    )

    new_session.set_cookie(response)

    # TODO: Implement storing additional session data. Either using redis or in the primary db, as this data is not that latency critical

    return RegisterResponse(
        user=PublicUser.parse_obj(new_user)
    )


@router.post('/logout')
async def logout(
    response: Response,
    session: Session[SessionData] = Depends(session_provider)
) -> LogoutResponse:
    await session.destroy(response)

    return LogoutResponse(
        success=True
    )


@router.get('/me')
async def me(
    session: Session[SessionData] = Depends(session_provider)
) -> PublicUser:
    user_predicate = await get_user_by_id(session.data.user_id)
    if user_predicate is None:
        raise USER_NOT_FOUND

    public_user = PublicUser(**user_predicate.dict())
    return public_user
