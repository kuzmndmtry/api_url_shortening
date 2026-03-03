import os
from redis import Redis

redis_url = os.getenv("REDIS_URL")

redis = Redis.from_url(
    redis_url,
    decode_responses=True
)