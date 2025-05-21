# ruff: noqa: B008
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.exceptions import CategoryNotFoundError, DuplicateCategoryError
from app.db.database import get_db
from app.schemas.category_schemas import CategoryCreate, CategoryResponse, CategoryUpdate
from app.schemas.user_schemas import UserResponse
from app.services.categories_service import CategoryService

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/", response_model=List[CategoryResponse], summary="Retrieve paginated list of categories")
async def get_all_categories(
    limit: int = Query(10, ge=1, le=100, description="Maximum number of categories to return"),
    offset: int = Query(0, ge=0, description="Number of categories to skip"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> List[CategoryResponse]:
    """Retrieve all categories (public access)."""
    return await CategoryService.get_all_categories(db, limit=limit, offset=offset)


@router.get("/{category_id}", response_model=CategoryResponse, summary="Get category by ID")
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> CategoryResponse:
    """Get category details by ID (public access)."""
    try:
        return await CategoryService.get_category_by_id(db, category_id)
    except CategoryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED, summary="Create a new category")
async def create_category(
    category_data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> CategoryResponse:
    """Create new category (Admin required)."""
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    try:
        return await CategoryService.create_category(db, category_data)
    except DuplicateCategoryError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.put("/{category_id}", response_model=CategoryResponse, summary="Update an existing category")
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> CategoryResponse:
    """Update existing category (Admin required)."""
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    try:
        return await CategoryService.update_category(db, category_id, category_data)
    except CategoryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except DuplicateCategoryError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a category")
async def delete_category(
    category_id: int,
    strict: bool = Query(False, description="If true, 404 when category doesn't exist; otherwise ignore"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> None:
    """Delete category (Admin required)."""
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    try:
        await CategoryService.delete_category(db, category_id, strict=strict)
    except CategoryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
