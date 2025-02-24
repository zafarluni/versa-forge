# app/api/routes/category_router.py

from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.schemas.category_schemas import CategoryCreate, CategoryResponse
from app.services.categories_service import CategoryService

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("/", response_model=CategoryResponse, status_code=201)
def create_category(category_data: CategoryCreate, db: Session = Depends(get_db)) -> CategoryResponse:
    """
    Create a new category.

    Args:
        category_data (CategoryCreate): The category details.
        db (Session): The database session.

    Returns:
        CategoryResponse: The created category.
    """
    return CategoryService.create_category(db, category_data)


@router.get("/", response_model=List[CategoryResponse])
def get_all_categories(limit: int = Query(10, ge=1), offset: int = Query(0, ge=0), 
                       db: Session = Depends(get_db)) -> List[CategoryResponse]:
    """
    Retrieve all categories.

    Args:
        db (Session): The database session.

    Returns:
        List[CategoryResponse]: A list of all categories.
    """
    return CategoryService.get_all_categories(db, limit, offset)


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)) -> CategoryResponse:
    """
    Retrieve a specific category by its ID.

    Args:
        category_id (int): The category ID.
        db (Session): The database session.

    Returns:
        CategoryResponse: The requested category.
    """
    return CategoryService.get_category_by_id(db, category_id)


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db), strict: bool = False) -> None:
    """
    Delete a category by its ID.

    If `strict` is `true`, it returns 404 if the category does not exist.
    Otherwise, it returns 204 regardless.
    """
    CategoryService.delete_category(db, category_id, strict=strict)
