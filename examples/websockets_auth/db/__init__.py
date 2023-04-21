from examples.websockets_auth.db.models.User import User
from examples.websockets_auth.hasher import ph

GENERIC_PASSWORD = 'password'


# TODO: Implement a proper db connection
users_db = [
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
            user for user in users_db if user.username == usernameOrEmail \
                or user.email == usernameOrEmail
        )
    except StopIteration:
        return None


async def get_user_by_id(user_id: int) -> User | None:
    try:
        return next(
            user for user in users_db if user.id == user_id
        )
    except StopIteration:
        return None
