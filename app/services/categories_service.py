# ========================
# Category Service (service/categories_service.py)
# ========================
from sqlalchemy.orm import Session
from app.db.models.database_models import Category
from app.db.schemas.category_schemas import CategoryCreate
from fastapi import HTTPException
from typing import List


class CategoryService:
    @staticmethod
    def create_category(db: Session, category_data: CategoryCreate):
        category = Category(
            name=category_data.name, description=category_data.description
        )
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def get_all_categories(db: Session) -> List[Category]:
        return db.query(Category).all()

    @staticmethod
    def get_category_by_id(db: Session, category_id: int):
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return category

    @staticmethod
    def delete_category(db: Session, category_id: int):
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        db.delete(category)
        db.commit()
        return {"message": "Category deleted successfully"}
