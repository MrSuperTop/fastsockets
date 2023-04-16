from fastsockets.auth.Session import BaseSessionData, current_session


class SessionData(BaseSessionData):
    ...


session_provider = current_session(SessionData)
