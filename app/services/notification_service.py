import logging

from app.config import settings

logger = logging.getLogger(__name__)


def send_notification(recipient: str, message: str) -> dict:
    """ইমেইল/SMS পাঠানোর জায়গা।

    এখনো কোনো প্রোভাইডার যুক্ত নেই। ডেভেলপমেন্টে মেসেজ লগে দেখাবে,
    প্রোডাকশনে এখানে SMTP বা SMS সার্ভিস যুক্ত করতে হবে।
    """
    if settings.debug:
        logger.info("[DEV] notification to %s: %s", recipient, message)

    return {"recipient": recipient, "status": "queued"}
