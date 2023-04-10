from importlib import import_module
from inspect import isclass
from pathlib import Path
from pkgutil import iter_modules

import uvicorn
from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from starlette.websockets import WebSocketDisconnect

from package.handlers import BaseActionHandler, NeededArgumentMapping

app = FastAPI()
handlers: dict[str, BaseActionHandler] = {}

package_dir = Path(__file__).resolve().parent.joinpath('./operations')
for (_, module_name, _) in iter_modules([str(package_dir.absolute())]):
    module = import_module(f"package.operations.{module_name}")
    for attribute_name in dir(module):
        attribute = getattr(module, attribute_name)

        if isclass(attribute) and BaseActionHandler in attribute.__bases__:
            operation_name = module.__name__.rpartition('.')[2]
            parsable_objects: NeededArgumentMapping = {}

            for arg_name, arg_type in attribute.__call__.__annotations__.items():
                if not isclass(arg_type) or BaseModel not in arg_type.__bases__:
                    continue

                parsable_objects[arg_name] = arg_type

            handlers[operation_name] = attribute(
                operation_name,
                parsable_objects
            )


@app.websocket('/ws')
async def main_ws(websocket: WebSocket):
    await websocket.accept()

    while True:
        try:
            json_message = await websocket.receive_json()
            print(f'{json_message} received')

            handler = handlers.get(json_message.get('op'))
            if handler is None:
                continue

            data_type = next(iter(handler.argument_object_mapping.values()))

            # TODO: Add proper validation..
            handler_result = await handler(data_type.parse_obj(json_message))
            await websocket.send_json(handler_result.dict())


        except WebSocketDisconnect:
            print('disconnected')


uvicorn.run(
    app,
    host='127.0.0.1',
    port=8080,
)
