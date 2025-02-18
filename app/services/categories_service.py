# ========================
# Category Service (service/categories_service.py)
# ========================
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app.db.models.database_models import Category
from app.db.schemas.category_schemas import CategoryCreate
from fastapi import HTTPException
from typing import List


class CategoryService:
    
    @staticmethod
    def create_category(db: Session, category_data: CategoryCreate):
        new_category = Category(name=category_data.name, description=category_data.description)
        db.add(new_category)
        try:
            db.commit()
            db.refresh(new_category)
            return new_category
        except IntegrityError:
            db.rollback()
        raise HTTPException(status_code=400, detail=f"Category with ${category_data.name} name already exists.")

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
