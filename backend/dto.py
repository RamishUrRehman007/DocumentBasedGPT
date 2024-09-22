from typing import Any, Dict, List, NewType, Optional, TypeVar, Union

from pydantic import UUID4, BaseModel, PositiveInt

ResponseT = TypeVar("ResponseT")
UserID = NewType("UserID", int)
FileID = NewType("FileID", UUID4)

JSON = Dict[str, Any]
UNION = Union


class Page(BaseModel):
    number: Optional[PositiveInt] = None
    size: Optional[PositiveInt] = None
    offset: int


class ErrorResponse(BaseModel):
    detail: str


class File(BaseModel):
    file_name: str
    mime_type: str
    file_size: int
    file_path: str
    file_hash: str


class FileFilter(BaseModel):
    file_name_original: Optional[str] = None


class FileUploadResponse(BaseModel):
    message: str
    files: List
    status: str


class FileStatus(BaseModel):
    status: str
