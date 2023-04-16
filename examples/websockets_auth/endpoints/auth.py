from argon2.exceptions import VerificationError
from fastapi import APIRouter, Depends, Response
from redis.asyncio import Redis

from examples.websockets_auth.db.models.User import User
from examples.websockets_auth.endpoints.exceptions import (
    INVALID_USER_CREDENTIALS,
    USER_ALREADY_EXISTS,
)
from examples.websockets_auth.get_redis import redis
from examples.websockets_auth.hasher import ph
from examples.websockets_auth.models.login import LoginInput, LoginResponse, PublicUser
from examples.websockets_auth.models.logout import LogoutResponse
from examples.websockets_auth.models.register import RegisterInput, RegisterResponse
from examples.websockets_auth.session import SessionData
from fastsockets.auth.Session import get_current_session_by_cookie
from fastsockets.auth.Session import Session

router = APIRouter()

GENERIC_PASSWORD = 'password'

# TODO: Implement a proper db connection
users = [
    User(
        id=5,
        email='bob@gmail.com',
        username='bob',
        password=ph.hash(GENERIC_PASSWORD),
        bio='hi its me'
    )
]


async def get_user(usernameOrEmail: str) -> User | None:
    try:
        return next(
            user for user in users if user.username == usernameOrEmail \
                or user.email == usernameOrEmail
        )
    except StopIteration:
        return None


@router.post('/login')
async def login(
    credentials: LoginInput,
    response: Response,
) -> LoginResponse:
    user_predicate = await get_user(credentials.usernameOrEmail)
    if user_predicate is None:
        raise INVALID_USER_CREDENTIALS

    try:
        ph.verify(user_predicate.password, credentials.password)
    except VerificationError:
        raise INVALID_USER_CREDENTIALS

    session_id = Session.generate_session_id()
    session = await Session.create_and_load(
        session_id,
        SessionData,
        user_predicate
    )

    session.set_cookie(response)

    return LoginResponse(
        user=PublicUser.parse_obj(user_predicate)
    )


@router.post('/register')
async def register(
    data: RegisterInput,
    response: Response,
) -> RegisterResponse:
    user_exists = any([await get_user(data.username), await get_user(data.email)])
    if user_exists:
        raise USER_ALREADY_EXISTS

    new_user = User.parse_obj({
        "id": users[-1].id + 1,
        **data.dict(),
    })
    new_user.password = ph.hash(data.password)
    users.append(new_user)

    session_id = Session.generate_session_id()

    session = await Session.create_and_load(
        session_id,
        SessionData,
        new_user
    )

    session.set_cookie(response)

    return RegisterResponse(
        user=PublicUser.parse_obj(new_user)
    )


@router.post('/logout')
async def logout(
    response: Response,
    session: Session[SessionData] = Depends(get_current_session_by_cookie)
) -> LogoutResponse:
    await session.destroy(response)

    return LogoutResponse(
        success=True
    )
