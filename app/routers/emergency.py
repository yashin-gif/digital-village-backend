from app.core.crud import READ_PUBLIC, build_crud_router
from app.dependencies import get_current_user
from app.models.emergency import Emergency
from app.schemas.common import partial_model
from app.schemas.emergency import EmergencyCreate, EmergencyResponse


# জরুরি সেবা সবাই দেখতে পারবে; রিপোর্ট করতে লগইন লাগবে (স্প্যাম ঠেকাতে)
router = build_crud_router(
    prefix="/emergency",
    tags=["Emergency"],
    model=Emergency,
    label="emergency",
    not_found="Emergency not found",
    create_schema=EmergencyCreate,
    update_schema=partial_model(EmergencyCreate, "EmergencyUpdate"),
    response_schema=EmergencyResponse,
    read_access=READ_PUBLIC,
    create_guard=get_current_user,
    default_limit=100,
    search_fields=[Emergency.title, Emergency.location, Emergency.contact_phone],
    filters={
        "status": (Emergency.status, "eq"),
        "emergency_type": (Emergency.emergency_type, "eq"),
    },
)
