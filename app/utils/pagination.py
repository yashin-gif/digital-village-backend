def paginate(
    items: list,
    page: int = 1,
    limit: int = 20,
):
    if page < 1:
        page = 1

    if limit < 1:
        limit = 20

    start = (page - 1) * limit
    end = start + limit

    return {
        "items": items[start:end],
        "page": page,
        "limit": limit,
        "total": len(items),
        "pages": (len(items) + limit - 1) // limit,
    }