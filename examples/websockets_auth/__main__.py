from pathlib import Path

import uvicorn
from fastapi import Depends, FastAPI

from examples.websockets_auth.routes.auth.endpoints import router as auth_router
from examples.websockets_auth.session import session_provider
from fastsockets import Handlers
from fastsockets.auth.Session import Session
from fastsockets.handlers.Executor import HandlersExecutor

app = FastAPI()
app.include_router(auth_router)

handlers_location = Path(__file__).parent.glob('**/handlers/*.py')
handlers = Handlers(handlers_location)


@app.websocket('/ws')
async def main_ws(
    handlers_executor: HandlersExecutor = Depends(handlers.get_executor),
    session: Session = Depends(session_provider)
) -> None:
    print(f'Established a connection: {session.data = }')

    await handlers_executor.accept()
    await handlers_executor.handle_messages()

    print('Disconnected!')


if __name__ == "__main__":
    uvicorn.run(
        'examples.websockets_auth.__main__:app',
        host='127.0.0.1',
        port=8080,
        reload=True
    )
