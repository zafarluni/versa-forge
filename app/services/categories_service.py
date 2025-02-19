# ========================
# Category Service (service/categories_service.py)
# ========================
from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session, load_only
from app.db.models.database_models import Category
from app.db.schemas.category_schemas import CategoryCreate, CategoryResponse


class CategoryService:
    @staticmethod
    def create_category(db: Session, category_data: CategoryCreate) -> CategoryResponse:
        normalized_name = category_data.name.strip().lower()  # Convert input name to lowercase

        existing_category = db.query(Category).filter(Category.name.ilike(normalized_name)).first()
        if existing_category:
            raise HTTPException(status_code=400, detail=f"Category with name '{category_data.name}' already exists.")

        new_category = Category(name=category_data.name.strip(), description=category_data.description)
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        return new_category




    @staticmethod
    def get_all_categories(db: Session) -> List[CategoryResponse]:
        categories = (
            db.query(Category)
            .options(load_only(getattr(Category, "id"), getattr(Category, "name"), getattr(Category, "description")))
            .all()
        )
        return [CategoryResponse.model_validate(category) for category in categories]

    @staticmethod
    def get_category_by_id(db: Session, category_id: int) -> CategoryResponse:
        category = db.query(Category).filter_by(id=category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return category

    @staticmethod
    def delete_category(db: Session, category_id: int) -> bool:
        category = db.query(Category).filter(Category.id == category_id).first()
        if category:
            db.delete(category)
            db.commit()
            return True        
        return False
