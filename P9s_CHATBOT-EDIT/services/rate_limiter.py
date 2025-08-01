#Path : services/rate_limiter.py
import time
from collections import defaultdict

REQUEST_LOG = defaultdict(list)

def is_rate_limited(user_id, limit=5, per=60):
    now = time.time()
    REQUEST_LOG[user_id] = [t for t in REQUEST_LOG[user_id] if now-t < per]
    if len(REQUEST_LOG[user_id]) >= limit:
        return True
    REQUEST_LOG[user_id].append(now)
    return False
