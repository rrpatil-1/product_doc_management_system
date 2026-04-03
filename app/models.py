from pydantic import BaseModel, Field, validator
from typing import Optional,List
from uuid import uuid4

class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str
    code: Optional[str] = None

class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error type or category")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[List[ErrorDetail]] = None
    code: Optional[str] = Field(None, description="Application-specific error code")
    timestamp: Optional[str] = None

class ProductBase(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(uuid4()), description="Unique identifier")
    name: str = Field(..., min_length=1, description="Product name")
    category: str = Field(..., min_length=1, description="Product category")
    description: str = Field(..., min_length=1, description="Product description")
    thumbnail_url:Optional[str] = Field(None, description="Thumbnail URL")
    price: float = Field(..., gt=0, description="Product price")
    discount: float = Field(default=0, ge=0, description="Discount amount")

    @validator('thumbnail_url')
    def validate_thumbnail_url(cls, v):
        if not v:
            return None
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Thumbnail URL must be a valid HTTP/HTTPS URL')
        return v

class ProductCreate(ProductBase):
    id: Optional[str] = None  # Allow user to provide or auto-generate

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    price: Optional[float] = None
    discount: Optional[float] = None

    @validator('price')
    def validate_price(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Price must be greater than 0')
        return v

    @validator('discount')
    def validate_discount(cls, v):
        if v is not None and v < 0:
            raise ValueError('Discount must be non-negative')
        return v

    @validator('thumbnail_url')
    def validate_thumbnail_url(cls, v):
        if v is not None:
            v = v.strip()
            if v and not v.startswith(('http://', 'https://')):
                raise ValueError('Thumbnail URL must be a valid HTTP/HTTPS URL')
            return v if v else None
        return v

class ProductInDB(ProductBase):
    id: str

class PaginatedProducts(BaseModel):
    products: List[ProductInDB]
    total: int
    skip: int
    limit: int