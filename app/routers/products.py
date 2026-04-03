import logging
from fastapi import APIRouter, HTTPException, Query, status
from app.models import ProductCreate, ProductUpdate, ProductInDB, PaginatedProducts, ErrorResponse, ErrorDetail
from app.crud import (
    create_product,
    get_products,
    get_product_by_id,
    update_product,
    delete_product,
    search_products
)
from typing import List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=ProductInDB, status_code=status.HTTP_201_CREATED, responses={
    201: {"description": "Product created successfully"},
    400: {"model": ErrorResponse, "description": "Bad request - validation error or duplicate ID"},
    422: {"model": ErrorResponse, "description": "Validation error"},
    500: {"model": ErrorResponse, "description": "Internal server error"}
})
async def create_new_product(product: ProductCreate):
    logger.info(f"API request to create product: {product.name}")
    # Check for duplicate id if provided
    if product.id:
        existing = await get_product_by_id(product.id)
        if existing:
            logger.warning(f"Attempt to create product with duplicate ID: {product.id}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=ErrorResponse(
                    error="conflict",
                    message="Product with this ID already exists",
                    code="PRODUCT_ID_EXISTS",
                    details=[ErrorDetail(field="id", message="ID already in use", code="DUPLICATE_ID")],
                    timestamp=datetime.utcnow().isoformat()
                ).dict()
            )
    try:
        result = await create_product(product)
        logger.info(f"Product created successfully: {result.id}")
        return result
    except ValueError as e:
        logger.warning(f"Validation error creating product: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(
                error="validation_error",
                message=str(e),
                code="VALIDATION_ERROR",
                timestamp=datetime.utcnow().isoformat()
            ).dict()
        )
    except Exception as e:
        logger.error(f"Error creating product: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error="internal_server_error",
                message="An unexpected error occurred while creating the product",
                code="INTERNAL_ERROR",
                timestamp=datetime.utcnow().isoformat()
            ).dict()
        )

@router.get("/", response_model=PaginatedProducts, responses={
    200: {"description": "Products retrieved successfully"},
    400: {"model": ErrorResponse, "description": "Bad request - invalid parameters"},
    500: {"model": ErrorResponse, "description": "Internal server error"}
})
async def read_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sort_field: str = Query("name", description="Field to sort by: name, category, price, discount"),
    sort_order: str = Query("asc", description="Sort order: asc or desc")
):
    logger.info(f"API request to read products with skip={skip}, limit={limit}, sort_field={sort_field}, sort_order={sort_order}")
    if sort_field not in ["name", "category", "price", "discount"]:
        logger.warning(f"Invalid sort field: {sort_field}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(
                error="validation_error",
                message=f"Invalid sort field: {sort_field}",
                code="INVALID_SORT_FIELD",
                details=[ErrorDetail(field="sort_field", message="Must be one of: name, category, price, discount", code="INVALID_ENUM_VALUE")],
                timestamp=datetime.utcnow().isoformat()
            ).dict()
        )
    if sort_order not in ["asc", "desc"]:
        logger.warning(f"Invalid sort order: {sort_order}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(
                error="validation_error",
                message=f"Invalid sort order: {sort_order}",
                code="INVALID_SORT_ORDER",
                details=[ErrorDetail(field="sort_order", message="Must be one of: asc, desc", code="INVALID_ENUM_VALUE")],
                timestamp=datetime.utcnow().isoformat()
            ).dict()
        )
    sort_order_int = 1 if sort_order == "asc" else -1
    try:
        from app.crud import get_products_count
        products = await get_products(skip=skip, limit=limit, sort_field=sort_field, sort_order=sort_order_int)
        total = await get_products_count()
        logger.info(f"Returning {len(products)} products out of {total}")
        return PaginatedProducts(products=products, total=total, skip=skip, limit=limit)
    except Exception as e:
        logger.error(f"Error retrieving products: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error="internal_server_error",
                message="An unexpected error occurred while retrieving products",
                code="INTERNAL_ERROR",
                timestamp=datetime.utcnow().isoformat()
            ).dict()
        )

# Search endpoint must come BEFORE the {product_id} route
@router.get("/search/", response_model=List[ProductInDB], responses={
    200: {"description": "Search completed successfully"},
    400: {"model": ErrorResponse, "description": "Bad request - invalid search parameters"},
    500: {"model": ErrorResponse, "description": "Internal server error"}
})
async def search_products_endpoint(
    q: str = Query(..., description="Search query"),
    field: Optional[str] = Query(None, description="Field to search in: name, category, description")
):
    logger.info(f"API request to search products with query='{q}', field={field}")
    if field and field not in ["name", "category", "description"]:
        logger.warning(f"Invalid search field: {field}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(
                error="validation_error",
                message=f"Invalid search field: {field}",
                code="INVALID_SEARCH_FIELD",
                details=[ErrorDetail(field="field", message="Must be one of: name, category, description", code="INVALID_ENUM_VALUE")],
                timestamp=datetime.utcnow().isoformat()
            ).dict()
        )
    try:
        products = await search_products(q, field)
        logger.info(f"Search returned {len(products)} products")
        return products
    except Exception as e:
        logger.error(f"Error searching products: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error="internal_server_error",
                message="An unexpected error occurred while searching products",
                code="INTERNAL_ERROR",
                timestamp=datetime.utcnow().isoformat()
            ).dict()
        )

@router.get("/{product_id}", response_model=ProductInDB, responses={
    200: {"description": "Product retrieved successfully"},
    404: {"model": ErrorResponse, "description": "Product not found"},
    500: {"model": ErrorResponse, "description": "Internal server error"}
})
async def read_product(product_id: str):
    logger.info(f"API request to read product {product_id}")
    try:
        product = await get_product_by_id(product_id)
        if not product:
            logger.warning(f"Product not found: {product_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorResponse(
                    error="not_found",
                    message=f"Product with ID '{product_id}' not found",
                    code="PRODUCT_NOT_FOUND",
                    details=[ErrorDetail(field="product_id", message="No product exists with this ID", code="RESOURCE_NOT_FOUND")],
                    timestamp=datetime.utcnow().isoformat()
                ).dict()
            )
        logger.info(f"Returning product {product_id}")
        return product
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving product {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error="internal_server_error",
                message="An unexpected error occurred while retrieving the product",
                code="INTERNAL_ERROR",
                timestamp=datetime.utcnow().isoformat()
            ).dict()
        )

@router.put("/{product_id}", response_model=ProductInDB, responses={
    200: {"description": "Product updated successfully"},
    404: {"model": ErrorResponse, "description": "Product not found"},
    422: {"model": ErrorResponse, "description": "Validation error"},
    500: {"model": ErrorResponse, "description": "Internal server error"}
})
async def update_existing_product(product_id: str, product: ProductUpdate):
    logger.info(f"API request to update product {product_id}")
    try:
        updated_product = await update_product(product_id, product)
        if not updated_product:
            logger.warning(f"Product not found or no changes: {product_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorResponse(
                    error="not_found",
                    message=f"Product with ID '{product_id}' not found",
                    code="PRODUCT_NOT_FOUND",
                    details=[ErrorDetail(field="product_id", message="No product exists with this ID", code="RESOURCE_NOT_FOUND")],
                    timestamp=datetime.utcnow().isoformat()
                ).dict()
            )
        logger.info(f"Product {product_id} updated successfully")
        return updated_product
    except ValueError as e:
        logger.warning(f"Validation error updating product {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(
                error="validation_error",
                message=str(e),
                code="VALIDATION_ERROR",
                timestamp=datetime.utcnow().isoformat()
            ).dict()
        )
    except Exception as e:
        logger.error(f"Error updating product {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error="internal_server_error",
                message="An unexpected error occurred while updating the product",
                code="INTERNAL_ERROR",
                timestamp=datetime.utcnow().isoformat()
            ).dict()
        )

@router.delete("/{product_id}", responses={
    204: {"description": "Product deleted successfully"},
    404: {"model": ErrorResponse, "description": "Product not found"},
    500: {"model": ErrorResponse, "description": "Internal server error"}
})
async def delete_existing_product(product_id: str):
    logger.info(f"API request to delete product {product_id}")
    try:
        deleted = await delete_product(product_id)
        if not deleted:
            logger.warning(f"Product not found for deletion: {product_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorResponse(
                    error="not_found",
                    message=f"Product with ID '{product_id}' not found",
                    code="PRODUCT_NOT_FOUND",
                    details=[ErrorDetail(field="product_id", message="No product exists with this ID", code="RESOURCE_NOT_FOUND")],
                    timestamp=datetime.utcnow().isoformat()
                ).dict()
            )
        logger.info(f"Product {product_id} deleted successfully")
        return {"message": "Product deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting product {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error="internal_server_error",
                message="An unexpected error occurred while deleting the product",
                code="INTERNAL_ERROR",
                timestamp=datetime.utcnow().isoformat()
            ).dict()
        )