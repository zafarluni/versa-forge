# app/api/routes/category_router.py

from typing import List, Annotated
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.exceptions import PermissionDeniedException
from app.db.database import get_db
from app.db.schemas.category_schemas import CategoryCreate, CategoryResponse, CategoryUpdate
from app.db.schemas.user_schemas import UserResponse
from app.services.categories_service import CategoryService

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/", response_model=List[CategoryResponse])
async def get_all_categories(
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> List[CategoryResponse]:
    """
    Retrieve all categories (public access).
    """
    return await CategoryService.get_all_categories(db, limit, offset)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> CategoryResponse:
    """
    Get category details by ID (public access).
    """
    return await CategoryService.get_category_by_id(db, category_id)


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> CategoryResponse:
    """
    Create new category (Admin required).
    """
    if not current_user.is_admin:
        raise PermissionDeniedException()

    return await CategoryService.create_category(db, category_data)


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> CategoryResponse:
    """
    Update existing category (Admin required).
    """
    if not current_user.is_admin:
        raise PermissionDeniedException()

    return await CategoryService.update_category(db, category_id, category_data)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
    strict: bool = Query(False, description="Enforce strict deletion (404 if not found)"),
) -> None:
    """
    Delete category (Admin required).
    """
    if not current_user.is_admin:
        raise PermissionDeniedException()

    await CategoryService.delete_category(db, category_id, strict=strict)
