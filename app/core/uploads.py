"""ছবি যাচাই ও সংরক্ষণ (প্রোফাইল, মসজিদ, প্রতিষ্ঠান, সংবাদ)।

ছবি সার্ভারে `uploads/` ফোল্ডারের ভেতরে থাকবে। ডেটাবেসে শুধু ওয়েব পথ রাখা হয়।
"""

import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

UPLOAD_ROOT = Path("uploads")
AVATAR_DIR = UPLOAD_ROOT / "avatars"

MAX_BYTES = 2 * 1024 * 1024  # ২ মেগাবাইট
ALLOWED_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
# ফাইলের প্রথম কয়েকটি বাইট দেখে আসল ধরন যাচাই (শুধু নাম বা হেডার নয়)
MAGIC = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG\r\n\x1a\n": "image/png",
}


def detect_type(head: bytes) -> str | None:
    if head[:12].startswith(b"RIFF") and head[8:12] == b"WEBP":
        return "image/webp"
    for signature, mime in MAGIC.items():
        if head.startswith(signature):
            return mime
    return None


async def _read_checked(file: UploadFile) -> tuple[bytes, str]:
    """আকার ও আসল ধরন যাচাই করে ফাইলের বাইট ও ফাইল এক্সটেনশন ফেরত দেয়।"""
    content = await file.read(MAX_BYTES + 1)

    if len(content) > MAX_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="ছবির আকার ২ মেগাবাইটের বেশি হতে পারবে না",
        )

    real_type = detect_type(content[:16])
    if real_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="শুধু JPG, PNG বা WEBP ছবি দেওয়া যাবে",
        )

    return content, ALLOWED_TYPES[real_type]


async def save_avatar(file: UploadFile, user_id: int) -> str:
    """প্রোফাইল ছবি যাচাই করে সংরক্ষণ করে, ওয়েব পথ ফেরত দেয়।"""
    content, extension = await _read_checked(file)

    AVATAR_DIR.mkdir(parents=True, exist_ok=True)

    # ফাইলের নাম আমরা বানাই, ব্যবহারকারীর দেওয়া নাম নয় (পথ ফাঁদ ঠেকাতে)
    filename = f"{user_id}-{uuid.uuid4().hex}{extension}"
    (AVATAR_DIR / filename).write_bytes(content)

    return f"/uploads/avatars/{filename}"


async def save_image(file: UploadFile, folder: str, prefix: str) -> str:
    """যেকোনো ছবি (মসজিদ, প্রতিষ্ঠান, সংবাদ) যাচাই করে সংরক্ষণ করে।

    folder: 'mosques', 'institutions', 'news'
    prefix: রেকর্ড আইডি (যেমন মসজিদের আইডি)
    """
    content, extension = await _read_checked(file)

    target_dir = UPLOAD_ROOT / folder
    target_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{prefix}-{uuid.uuid4().hex}{extension}"
    (target_dir / filename).write_bytes(content)

    return f"/uploads/{folder}/{filename}"


def delete_file(url: str | None) -> None:
    """uploads ফোল্ডারের যেকোনো ছবি মুছে ফেলে (নিরাপদ পথ যাচাই সহ)।"""
    if not url or not url.startswith("/uploads/"):
        return
    path = UPLOAD_ROOT / url.removeprefix("/uploads/")
    if path.exists() and path.is_file():
        path.unlink()


def delete_avatar(url: str | None) -> None:
    """পুরনো প্রোফাইল ছবি মুছে ফেলে (রাউটারের আগের কোড এটা ব্যবহার করে)।"""
    delete_file(url)