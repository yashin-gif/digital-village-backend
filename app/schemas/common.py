from typing import Any, Optional

from pydantic import BaseModel, create_model


def partial_model(base: type[BaseModel], name: str) -> type[BaseModel]:
    """আপডেটের জন্য: সব ফিল্ড ঐচ্ছিক। শুধু যে ফিল্ড পাঠানো হবে সেটাই বদলাবে।"""
    fields: dict[str, Any] = {
        field_name: (Optional[field.annotation], None)
        for field_name, field in base.model_fields.items()
    }
    return create_model(name, **fields)
