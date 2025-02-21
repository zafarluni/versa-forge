from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.schemas.category_schemas import CategoryCreate, CategoryResponse
from app.services.categories_service import CategoryService

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(category_data: CategoryCreate, db: Session=Depends(get_db)) -> CategoryResponse:
    return CategoryService.create_category(db, category_data)


@router.get("/", response_model=List[CategoryResponse])
def get_all_categories(db: Session=Depends(get_db)) -> List[CategoryResponse]:
    return CategoryService.get_all_categories(db)


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session=Depends(get_db)) -> CategoryResponse:
    return CategoryService.get_category_by_id(db, category_id)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session=Depends(get_db), strict: bool = False) -> Response:
    deleted = CategoryService.delete_category(db, category_id)
    if strict and not deleted:
        raise HTTPException(status_code=404, detail="Category not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
