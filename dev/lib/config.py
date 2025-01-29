from datetime import datetime, timezone

UTC_TZ = timezone.utc


def get_current_time():
    return datetime.now(UTC_TZ)
