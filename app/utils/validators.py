import re

# বাংলাদেশের মোবাইল: 01 দিয়ে শুরু, মোট ১১ সংখ্যা (013-019)
BD_MOBILE_PATTERN = re.compile(r"^01[3-9]\d{8}$")


def normalize_phone(value: str) -> str:
    """স্পেস, ড্যাশ ও +880 বাদ দিয়ে 01XXXXXXXXX বানায়।"""
    digits = re.sub(r"[\s\-]", "", value or "")

    if digits.startswith("+880"):
        digits = "0" + digits[4:]
    elif digits.startswith("880"):
        digits = "0" + digits[3:]

    return digits


def validate_bd_phone(value: str) -> str:
    """বৈধ হলে স্বাভাবিক রূপে ফেরত দেয়, না হলে ValueError।"""
    phone = normalize_phone(value)

    if not BD_MOBILE_PATTERN.match(phone):
        raise ValueError("মোবাইল নম্বর ০১ দিয়ে শুরু হয়ে ১১ সংখ্যার হতে হবে (যেমন 017XXXXXXXX)")

    return phone