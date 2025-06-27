from fastapi import HTTPException
from pydantic import BaseModel
from typing import Type


def raise_http_exception(status: int, response: Type[BaseModel]):
    raise HTTPException(
        status_code=status,
        detail=response.dict()
    )
