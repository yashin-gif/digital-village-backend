from app.core.crud import READ_PUBLIC, build_crud_router
from app.models.place import Place
from app.schemas.common import partial_model
from app.schemas.place import PlaceCreate, PlaceResponse


router = build_crud_router(
    prefix="/places",
    tags=["Places"],
    model=Place,
    label="place",
    not_found="Place not found",
    create_schema=PlaceCreate,
    update_schema=partial_model(PlaceCreate, "PlaceUpdate"),
    response_schema=PlaceResponse,
    read_access=READ_PUBLIC,
    search_fields=[Place.name, Place.place_type, Place.address],
)
