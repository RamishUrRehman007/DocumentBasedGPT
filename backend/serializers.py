from typing import Optional

import dto
from fastapi import Query
from fastapi.exceptions import RequestValidationError
from pydantic import PositiveInt
from pydantic.error_wrappers import ErrorWrapper


def page_from_query_param(
    page_number: Optional[PositiveInt] = Query(
        None,
        title="Page number",
        description=(
            "A positive integer to indicate which page of the results should be fetched. "
            "This parameter should be passed together with a page_size value."
        ),
    ),
    page_size: Optional[PositiveInt] = Query(
        None,
        title="Page size",
        description=(
            "A positive integer to indicate the number of results to be fetched per page. "
            "This parameter should be passed together with a page_number value."
        ),
    ),
) -> Optional[dto.Page]:
    if page_number is None and page_size is None:
        return None

    offset = 0
    if page_number and page_size:
        offset = (page_number - 1) * page_size

    try:
        return dto.Page(number=page_number, size=page_size, offset=offset)
    except ValueError as error:
        raise RequestValidationError(
            errors=[ErrorWrapper(exc=error, loc=("query.page"))]
        )
