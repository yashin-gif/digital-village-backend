def clean_text(value: str | None) -> str | None:
    if value is None:
        return None

    return " ".join(value.strip().split())


def normalize_blood_group(
    blood_group: str,
) -> str:
    return blood_group.strip().upper()