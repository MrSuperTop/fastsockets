from fastapi import Cookie

from fastsockets.exceptions import ALREADY_AUTHENICATED


def not_authenticated(
    session_id: str | None = Cookie(default=None)
):
    if session_id is not None:
        raise ALREADY_AUTHENICATED
