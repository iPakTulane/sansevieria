import redis
import logging
from app.config import settings

logger = logging.getLogger("REDIS_CLIENT")

def get_redis_connection():
    try:
        r = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD or None,
            db=settings.REDIS_DB,
            decode_responses=True # Automatically decode to strings
        )
        r.ping()
        return r
    except redis.ConnectionError as e:
        logger.error(f"[REDIS] Connection error: {e}")
        return None

redis_client = get_redis_connection()
