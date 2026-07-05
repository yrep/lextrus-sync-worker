from pydantic import BaseModel
from typing import List, Optional


class PropertyItem(BaseModel):
    reference: str
    updatedAt: Optional[str] = None
    createdAt: Optional[str] = None

    class Config:
        extra = "allow"


class ApiResponse(BaseModel):
    total: int
    limit: int
    offset: int
    data: List[PropertyItem]
