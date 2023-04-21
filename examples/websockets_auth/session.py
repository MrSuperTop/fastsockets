from examples.websockets_auth.get_redis import get_redis
from fastsockets.auth.Session import BaseSessionData
from fastsockets.auth.SessionProvider import EXAMPLE_SIGN_SECRET, SessionProvider


class SessionData(BaseSessionData):
    ...


session_provider = SessionProvider(SessionData, EXAMPLE_SIGN_SECRET, get_redis)
