"""লগইনে ভুল চেষ্টা সীমিত করা।

প্রতিটি লগইন আইডি (ইউজারনেম/মোবাইল) ও আইপির জন্য ভুলের সংখ্যা গোনা হয়।
নির্দিষ্ট সংখ্যা পার হলে সময়ের জন্য বন্ধ থাকে।

নোট: এটি মেমোরিতে চলে। সার্ভার একাধিক প্রসেসে চললে বা রিস্টার্ট হলে
গণনা আলাদা হবে। প্রোডাকশনে Redis দিয়ে বদলানো যাবে।
"""

import threading
import time
from collections import defaultdict, deque

# সীমা
MAX_FAILURES = 5          # এই সংখ্যক ভুলের পর বন্ধ
WINDOW_SECONDS = 15 * 60  # ভুল গোনার সময়সীমা (১৫ মিনিট)
LOCK_SECONDS = 15 * 60    # বন্ধ থাকার সময় (১৫ মিনিট)
IP_MAX_FAILURES = 30      # একই আইপি থেকে এতগুলো ভুলের পর বন্ধ

_lock = threading.Lock()
_failures: dict[str, deque] = defaultdict(deque)   # key -> ভুলের সময়গুলো
_locked_until: dict[str, float] = {}                # key -> কখন পর্যন্ত বন্ধ


def _prune(key: str, now: float) -> None:
    attempts = _failures[key]
    while attempts and now - attempts[0] > WINDOW_SECONDS:
        attempts.popleft()


def is_locked(key: str) -> int:
    """বন্ধ থাকলে কত সেকেন্ড বাকি তা ফেরত দেয়, না থাকলে 0।"""
    now = time.time()
    with _lock:
        until = _locked_until.get(key, 0)
        if until > now:
            return int(until - now) + 1
        if key in _locked_until:
            del _locked_until[key]
        return 0


def record_failure(key: str, limit: int) -> None:
    now = time.time()
    with _lock:
        _prune(key, now)
        _failures[key].append(now)
        if len(_failures[key]) >= limit:
            _locked_until[key] = now + LOCK_SECONDS
            _failures[key].clear()


def clear_failures(key: str) -> None:
    with _lock:
        _failures.pop(key, None)
        _locked_until.pop(key, None)