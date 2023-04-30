from .handlers.BaseActionHandler import BaseActionHandler as BaseActionHandler
from .handlers.Executor import HandlersExecutor as HandlersExecutor
from .handlers.handler import handler as handler
from .handlers.Handlers import Handlers as Handlers
from .types.BaseMessage import BaseMessage as BaseMessage

# TODO: Session auth with redis and custom providers.
# TODO: Error handling and proper responses? Read more.
# TODO: A testing suite
# TODO: Lib name? What about "quicksocket"? Like blitzstockets or even quicksockets, something alike.
# TODO: Try using orjson where possible just for the sake of it
# TODO: Example Config class implementation https://docs.pydantic.dev/usage/settings/
# TODO: https://dev.to/idanarye/are-there-any-api-specification-formats-for-websockets-2mkk

# TODO: Multiple concurennt session support through a custom class
# The handle will have access to a custom class object that manager all websocket
# connections that have been created by the same user with active sessions and
# provides an API to conveniently send messages to all of them.
# This will required the depency system to work properly as well as a custom
# connection class to simplify the API implementation under the hood
# Check this out: https://realpython.com/async-io-python/#using-a-queue
