from pathlib import Path

import uvicorn
from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect

from package.load_handlers import load_handlers

app = FastAPI()

# TODO: Authenticated routes
# TODO: Dependency injection
# TODO: Publish to pip
# TODO: Clean up

# TODO: A whole middleware for this purpose
handlers_locations = Path(__file__).resolve().parent.joinpath('').glob('**/handlers')
handlers = load_handlers(handlers_locations)


@app.websocket('/ws')
async def main_ws(websocket: WebSocket):
    await websocket.accept()

    while True:
        try:
            json_message = await websocket.receive_json()

            handler = handlers.get(json_message.get('action'))
            if handler is None:
                continue

            message_data = handler.data_validator.parse_obj(json_message)

            handler_result = await handler(message_data.payload)
            await websocket.send_json(handler_result.dict())


        except WebSocketDisconnect:
            print('disconnected')


if __name__ == "__main__":
    uvicorn.run(
        'package.__main__:app',
        host='127.0.0.1',
        port=8080,
        reload=True
    )
