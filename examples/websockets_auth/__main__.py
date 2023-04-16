from pathlib import Path

import uvicorn
from fastapi import Depends
from fastapi import FastAPI, Cookie
from fastsockets.auth.Session import Session, SessionData
from examples.websockets_auth.endpoints.auth import router as auth_router
from fastsockets import HandlersExecutor, Handlers
from examples.websockets_auth.get_redis import redis
from fastsockets.auth.Session import get_current_session_by_cookie
app = FastAPI()
app.include_router(auth_router)

handlers_locations = Path(__file__).parent.glob('**/handlers/*.py')
handlers = Handlers(handlers_locations)


@app.websocket('/ws')
async def main_ws(
        handlers_executor: HandlersExecutor = Depends(handlers.get_executor),
        session: Session[SessionData] = Depends(get_current_session_by_cookie),
) -> None:
    print(session.user.username, 'connected')
    await handlers_executor.accept()
    await handlers_executor.handle_messages()

    # * Disconnected logic
    print('Disconnected!')


if __name__ == "__main__":
    uvicorn.run(
        'examples.websockets_auth.__main__:app',
        host='127.0.0.1',
        port=8080,
        reload=True
    )
