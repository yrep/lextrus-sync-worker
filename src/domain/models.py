from pydantic import BaseModel, Field
from typing import List, Optional


class PropertyItem(BaseModel):
    reference: str
    updatedAt: Optional[str] = None
    createdAt: Optional[str] = None

    model_config = {
        "extra": "allow"   # id, title, price, ...
    }


class ApiResponse(BaseModel):
    total: int
    limit: int
    offset: int
    data: List[PropertyItem] = Field(alias='items')

    model_config = {
        "populate_by_name": True
    }