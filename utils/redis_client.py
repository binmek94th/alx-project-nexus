import redis

from alx_project_nexus.settings import REDIS_URL

redis_client = redis.Redis.from_url(REDIS_URL)
