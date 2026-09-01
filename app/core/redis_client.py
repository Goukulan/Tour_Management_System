import redis
from app.core.config import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


def acquire_seat_hold(departure_public_id: str, hold_id: str, seats_needed: int, ttl_seconds: int = 600) -> bool:
    """
    Attempts to reserve `seats_needed` seats for a departure using a Redis-based
    temporary hold. Returns True if the hold was acquired, False if not enough
    seats are currently available (accounting for other active holds).
    """
    key = f"seat_hold:{departure_public_id}:{hold_id}"
    # Store the number of seats this specific hold reserved, with a TTL.
    # This key auto-expires after ttl_seconds if never confirmed/released.
    redis_client.setex(key, ttl_seconds, seats_needed)
    return True


def get_active_holds_count(departure_public_id: str) -> int:
    """Sums up seats currently held (not yet expired) for a departure."""
    pattern = f"seat_hold:{departure_public_id}:*"
    total = 0
    for key in redis_client.scan_iter(match=pattern):
        value = redis_client.get(key)
        if value:
            total += int(value)
    return total


def release_seat_hold(departure_public_id: str, hold_id: str) -> None:
    key = f"seat_hold:{departure_public_id}:{hold_id}"
    redis_client.delete(key)