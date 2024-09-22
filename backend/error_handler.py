import logging
from typing import Mapping, Optional, Type

import exceptions
from fastapi import Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


async def exception_handler(request: Optional[Request], exc: Exception) -> JSONResponse:
    exception_to_http_error_mapping: Mapping[Type[Exception], int] = {
        exceptions.EntityNotFoundError: status.HTTP_404_NOT_FOUND,
        exceptions.DuplicateEntityError: status.HTTP_409_CONFLICT,
        exceptions.UnauthorizeError: status.HTTP_401_UNAUTHORIZED,
    }

    # We care for inheritance, so we need to check the error using isinstance(). A direct lookup
    # using e.g. exception_to_http_error_mapping.get(type(exc)) will not give correct results.
    for basetype, status_code in exception_to_http_error_mapping.items():
        if isinstance(exc, basetype):
            return JSONResponse(
                status_code=status_code,
                content={"message": exc.message, "errorCode": exc.custom_error_code},
            )
            # return JSONResponse(status_code=status_code, content={"detail": str(exc)})

    # catch-all
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": str(exc)}
    )
