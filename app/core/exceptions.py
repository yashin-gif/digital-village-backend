from fastapi import HTTPException, status


def unauthorized(message: str = "Authentication required"):
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=message,
    )


def forbidden(message: str = "You do not have permission"):
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=message,
    )


def not_found(message: str = "Resource not found"):
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=message,
    )