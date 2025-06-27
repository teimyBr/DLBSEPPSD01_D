from pydantic import BaseModel
from typing import Optional


class UploadResponse(BaseModel):
    status: str
    bucket: str
    file: str


class PresignedUrlResponse(BaseModel):
    status: str
    url: Optional[str]
    expiration_hours: int
