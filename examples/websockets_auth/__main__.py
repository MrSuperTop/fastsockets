from pathlib import Path

import uvicorn
from fastapi import Depends, FastAPI

from examples.websockets_auth.routes.auth.endpoints import router as auth_router
from examples.websockets_auth.session import session_provider
from fastsockets import AuthHandlers, SessionHandlersExecutor, Session

app = FastAPI()
app.include_router(auth_router)

handlers_location = Path(__file__).parent.glob('**/handlers/*.py')
handlers = AuthHandlers(handlers_location, session_provider)


@app.websocket('/ws')
async def main_ws(
    handlers_executor: SessionHandlersExecutor = Depends(handlers.get_executor),
    session: Session = Depends(session_provider)
) -> None:
    print(f'Established a connection: {session.data = }')
    async with handlers_executor:
        await handlers_executor.handle_messages()

    print('Disconnected!')


if __name__ == "__main__":
    uvicorn.run(
        'examples.websockets_auth.__main__:app',
        host='127.0.0.1',
        port=8080,
        reload=True
    )
