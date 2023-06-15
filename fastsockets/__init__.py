from .auth.Session import Session as Session
from .handlers.auth.AuthHandlers import AuthHandlers as AuthHandlers
from .handlers.auth.SessionExecutor import \
    SessionHandlersExecutor as SessionHandlersExecutor
from .handlers.BaseActionHandler import BaseActionHandler as BaseActionHandler
from .handlers.Executor import HandlersExecutor as HandlersExecutor
from .handlers.handler import handler as handler
from .handlers.Handlers import Handlers as Handlers
from .types.BaseMessage import BaseMessage as BaseMessage

# TODO: Error handling and proper responses? Read more.
# TODO: A test suite
# TODO: Logging
# TODO: Lib name? What about "quicksocket"? Like blitzstockets or even quicksockets, something alike.
# TODO: Try using orjson where possible just for the sake of it
# TODO: Example Config class implementation https://docs.pydantic.dev/usage/settings/

# TODO: https://dev.to/idanarye/are-there-any-api-specification-formats-for-websockets-2mkk
# Generate clients on the go using some tooling or maybe come up with something on my own.
# Preferrably for python and ts

# https://github.com/python-websockets/websockets/issues/653
# How is starlett unilizing the websockets package under the hood and is it possible to
# use the broadcast method from websockets instead of reinventing the wheel?
# https://websockets.readthedocs.io/en/stable/topics/broadcast.html#broadcasting-messages
# As of right now, we are not bothering much and usign this method on top of the
# barebones API the scarlett providers: https://websockets.readthedocs.io/en/stable/topics/broadcast.html#the-concurrent-way
# Should look into that...

# Interesting project over here, could use the postgres LISTEN/NOTIFY API: https://pypi.org/project/broadcaster/
# Look up the ideas and possibly try to implement something like that from scratch
