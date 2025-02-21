# ========================
# Category Service (service/categories_service.py)
# ========================
from typing import List
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.database_models import Category
from app.db.schemas.category_schemas import CategoryCreate, CategoryResponse

class CategoryService:
    @staticmethod
    def create_category(db: Session, category_data: CategoryCreate) -> CategoryResponse:
        normalized_name = category_data.name.strip().lower()
        stmt = select(Category).where(Category.name.ilike(normalized_name))
        existing_category = db.execute(stmt).scalar_one_or_none()
        if existing_category:
            raise HTTPException(status_code=400, detail=f"Category '{category_data.name}' already exists.")
        new_category = Category(name=category_data.name.strip(), description=category_data.description)
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        return CategoryResponse.model_validate(new_category)

    @staticmethod
    def get_all_categories(db: Session) -> List[CategoryResponse]:
        stmt = select(Category)
        categories = db.execute(stmt).scalars().all()
        return [CategoryResponse.model_validate(category) for category in categories]

    @staticmethod
    def get_category_by_id(db: Session, category_id: int) -> CategoryResponse:
        stmt = select(Category).where(Category.id == category_id)
        category = db.execute(stmt).scalar_one_or_none()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return CategoryResponse.model_validate(category)

    @staticmethod
    def delete_category(db: Session, category_id: int) -> bool:
        stmt = select(Category).where(Category.id == category_id)
        category = db.execute(stmt).scalar_one_or_none()
        if category:
            db.delete(category)
            db.commit()
            return True
        return False
