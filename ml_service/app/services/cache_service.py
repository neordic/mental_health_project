import redis
import json
from typing import Optional
from ml_service.app.core.config import settings
from ml_service.app.schemas.auth import UserRead
from ml_service.app.core.logger import get_logger

logger = get_logger("cache")

r = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=2,
    decode_responses=True
)

PROFILE_KEY = "user:profile:{}"
CREDITS_KEY = "user:credits:{}"


def get_user_profile_cached(user_id: int) -> Optional[UserRead]:
    try:
        key = PROFILE_KEY.format(user_id)
        if r.exists(key):
            logger.info(f"[REDIS][NOEXPIRE] HIT: user profile (user_id={user_id})")
            return UserRead(**r.hgetall(key))
        logger.info(f"[REDIS][NOEXPIRE] MISS: user profile (user_id={user_id})")
    except Exception:
        logger.exception(f"[REDIS][ERROR] Failed to get user profile (user_id={user_id})")
    return None


def set_user_profile_cached(user_id: int, profile: UserRead | dict):
    try:
        key = PROFILE_KEY.format(user_id)
        data = profile.model_dump() if isinstance(profile, UserRead) else profile
        r.hset(key, mapping=data)
        logger.info(f"[REDIS][NOEXPIRE] SET: user profile (user_id={user_id})")
    except Exception:
        logger.exception(f"[REDIS][ERROR] Failed to set user profile (user_id={user_id})")


def get_user_credits_cached(user_id: int) -> Optional[dict]:
    try:
        key = CREDITS_KEY.format(user_id)
        if r.exists(key):
            logger.info(f"[REDIS][NOEXPIRE] HIT: user credits (user_id={user_id})")
            data = r.hgetall(key)
            return {
                "available_credits": int(data.get("available_credits", 0)),
                "frozen_credits": int(data.get("frozen_credits", 0))
            }
        logger.info(f"[REDIS][NOEXPIRE] MISS: user credits (user_id={user_id})")
    except Exception:
        logger.exception(f"[REDIS][ERROR] Failed to get user credits (user_id={user_id})")
    return None


def set_user_credits_cached(user_id: int, credits: dict):
    try:
        key = CREDITS_KEY.format(user_id)
        r.hset(key, mapping=credits)
        logger.info(f"[REDIS][NOEXPIRE] SET: user credits (user_id={user_id})")
    except Exception:
        logger.exception(f"[REDIS][ERROR] Failed to set user credits (user_id={user_id})")


def invalidate_user_cache(user_id: int):
    try:
        r.delete(PROFILE_KEY.format(user_id))
        r.delete(CREDITS_KEY.format(user_id))
        logger.info(f"[REDIS][NOEXPIRE] DELETE: user cache (user_id={user_id})")
    except Exception:
        logger.exception(f"[REDIS][ERROR] Failed to invalidate cache (user_id={user_id})")


def get_user_history_cached(user_id: int) -> Optional[list]:
    key = f"user:history:{user_id}"
    try:
        if r.exists(key):
            logger.info(f"[REDIS][NOEXPIRE] HIT: user history (user_id={user_id})")
            return json.loads(r.get(key))
        logger.info(f"[REDIS][NOEXPIRE] MISS: user history (user_id={user_id})")
    except Exception:
        logger.exception(f"[REDIS][ERROR] Failed to get user history (user_id={user_id})")
    return None


def set_user_history_cached(user_id: int, history: list):
    key = f"user:history:{user_id}"
    try:
        r.set(key, json.dumps(history))
        logger.info(f"[REDIS][NOEXPIRE] SET: user history (user_id={user_id})")
    except Exception:
        logger.exception(f"[REDIS][ERROR] Failed to set user history (user_id={user_id})")

