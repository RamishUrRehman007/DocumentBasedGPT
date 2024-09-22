from typing import List, Optional

import dto
from domains import file_domain
from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Path,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

router = APIRouter()


@router.post(
    "/files",
    response_model=dto.FileUploadResponse,
    tags=["files"],
)
async def create_file(
    files: List[UploadFile] = File(...),
) -> dto.FileUploadResponse:
    """
    Create view for uploading a new file.

    \f
    :return:
    """
    return await file_domain.create_file(
        files=files,
    )


@router.get(
    "/files/status",
    response_model=dto.FileStatus,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": dto.ErrorResponse,
            "description": "File not found.",
        },
    },
    tags=["files"],
)
async def get_file_status() -> dto.FileStatus:
    """
    Detail view for getting File Status

    \f
    :return:
    """

    file = await file_domain.file_status()
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found."
        )

    return file


@router.get(
    "/files",
    response_model=List[dto.File],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": dto.ErrorResponse,
            "description": "File not found.",
        },
    },
    tags=["files"],
)
async def get_files() -> List[dto.File]:
    """
    Detail view for getting one File by ID.

    \f
    :return:
    """

    file = await file_domain.find_one()
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found."
        )

    return file
