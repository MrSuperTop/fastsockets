from examples.auth.redis import redis
from fastsockets.auth.Session import BaseSessionData, current_session


class SessionData(BaseSessionData):
    ...


session_provider = current_session(redis, SessionData)
