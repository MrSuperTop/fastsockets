from redis import asyncio as aioredis

redis_instance = aioredis.from_url('redis://localhost:6379')


def get_redis() -> aioredis.Redis:
    return redis_instance
