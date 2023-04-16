from fastsockets.auth.Session import BaseSessionData
from fastsockets.auth.SessionProvider import SessionProvider, EXAMPLE_SIGN_SECRET


class SessionData(BaseSessionData):
    ...


session_provider = SessionProvider(SessionData, EXAMPLE_SIGN_SECRET)
