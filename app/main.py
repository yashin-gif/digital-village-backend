from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import DEFAULT_SECRET_KEY, settings
from app.database import Base, engine
from app.models import Family, Person, User  # noqa: F401  (সব টেবিল রেজিস্টার করতে)
from app.routers.auth import router as auth_router
from app.routers.families import router as families_router
from app.routers.people import router as people_router
from app.routers.education import router as education_router
from app.routers.blood import router as blood_router
from app.routers.institutions import router as institutions_router
from app.routers.mosque import router as mosques_router
from app.routers.place import router as places_router
from app.routers.help_requests import router as help_requests_router
from app.routers.zakat import router as zakat_router
from app.routers.community import router as community_router
from app.routers.news import router as news_router
from app.routers.announcement import router as announcements_router
from app.routers.emergency import router as emergency_router
from app.routers.public import router as public_router
from app.routers.admin import router as admin_router
from app.routers.bayan import bayan_router, kitab_progress_router, kitab_router
from app.routers.my import router as my_router


# প্রোডাকশনে (DEBUG=false) ডিফল্ট সিক্রেট কী দিয়ে চালানো যাবে না
if not settings.debug and settings.secret_key == DEFAULT_SECRET_KEY:
    raise RuntimeError("SECRET_KEY must be set in .env when DEBUG=false")

# টেবিল তৈরি (নতুন ডেটাবেসে)। বিদ্যমান ডেটাবেসে বদল আনতে alembic ব্যবহার করুন।
Base.metadata.create_all(bind=engine)

# প্রোফাইল ছবির ফোল্ডার আগে থেকে থাকতে হবে, নইলে mount ব্যর্থ হয়
Path("uploads/avatars").mkdir(parents=True, exist_ok=True)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A community management and information platform for villages.",
)

# ফ্রন্টএন্ড (Vite) থেকে API ডাকার অনুমতি
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count"],
)

# প্রোফাইল ছবি দেখানো (শুধু uploads ফোল্ডার)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# Authentication
app.include_router(auth_router)

# Families & People
app.include_router(families_router)
app.include_router(people_router)

# Education
app.include_router(education_router)

# Blood
app.include_router(blood_router)

# Institutions
app.include_router(institutions_router)

# Mosques
app.include_router(mosques_router)

# Places
app.include_router(places_router)

# Help & Welfare
app.include_router(help_requests_router)
app.include_router(zakat_router)

# Community
app.include_router(community_router)

# Information
app.include_router(news_router)
app.include_router(announcements_router)

# Emergency
app.include_router(emergency_router)

# Public
app.include_router(public_router)

# Bayan & Kitab
app.include_router(bayan_router)
app.include_router(kitab_router)
app.include_router(kitab_progress_router)

# আমার তথ্য (লগইন করা সদস্য)
app.include_router(my_router)

# Admin
app.include_router(admin_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to Digital Village API",
        "version": settings.app_version,
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.app_name,
    }