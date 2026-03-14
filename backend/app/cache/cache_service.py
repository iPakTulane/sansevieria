import json
import logging
from app.cache.redis_client import redis_client

logger = logging.getLogger("CACHE_SERVICE")

class CacheService:
    @staticmethod
    def get_cache(key: str):
        if not redis_client:
            return None
        try:
            val = redis_client.get(key)
            if val:
                logger.info(f"[CACHE] HIT for key={key}")
                return json.loads(val)
            logger.info(f"[CACHE] MISS for key={key}")
        except Exception as e:
            logger.error(f"[CACHE] Error reading key={key}: {e}")
        return None

    @staticmethod
    def set_cache(key: str, value: dict | list, ttl: int = 300):
        if not redis_client:
            return False
        try:
            redis_client.setex(key, ttl, json.dumps(value))
            logger.info(f"[CACHE] SET key={key} ttl={ttl}")
            return True
        except Exception as e:
            logger.error(f"[CACHE] Error setting key={key}: {e}")
            return False

    @staticmethod
    def invalidate_cache(key: str):
        if not redis_client:
            return False
        try:
            redis_client.delete(key)
            logger.info(f"[CACHE] INVALIDATED key={key}")
            return True
        except Exception as e:
            logger.error(f"[CACHE] Error invalidating key={key}: {e}")
            return False
