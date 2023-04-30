from pathlib import Path

import uvicorn
from fastapi import Depends, FastAPI

from fastsockets import Handlers, HandlersExecutor

app = FastAPI()

handlers_locations = Path(__file__).parent.glob('**/handlers/*.py')
handlers = Handlers(handlers_locations)


@app.websocket('/ws')
async def main_ws(
    handlers_executor: HandlersExecutor = Depends(handlers.get_executor)
) -> None:
    async with handlers_executor:
        await handlers_executor.handle_messages()

    # * Disconnected logic
    print('Disconnected!')


if __name__ == "__main__":
    uvicorn.run(
        'examples.simple_decorator_based.__main__:app',
        host='127.0.0.1',
        port=8080,
        reload=True
    )
