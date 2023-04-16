from redis import asyncio as aioredis
from fastsockets.auth.Session import Session

redis = aioredis.from_url('redis://localhost:6379')
Session.redis = redis
