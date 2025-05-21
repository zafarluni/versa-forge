import logging
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import CategoryNotFoundError, DatabaseError, DuplicateCategoryError
from app.db.models.database_models import Category
from app.schemas.category_schemas import CategoryCreate, CategoryResponse, CategoryUpdate

logger = logging.getLogger(__name__)


class CategoryService:
    @staticmethod
    async def create_category(db: AsyncSession, category_data: CategoryCreate) -> CategoryResponse:
        """
        Create a new category. Raises DuplicateCategoryError if name exists.
        """
        try:
            async with db.begin_nested():
                name = category_data.name.strip()
                await CategoryService._validate_unique(db, name)
                new_cat = Category(name=name, description=category_data.description)
                db.add(new_cat)
                await db.flush()  # send INSERT to DB
                await db.refresh(new_cat)  # load generated fields
            return CategoryResponse.model_validate(new_cat)
        except Exception as e:
            if not isinstance(e, DuplicateCategoryError):
                logger.error("create_category error", exc_info=True)
                raise DatabaseError(f"Failed to create category: {e}") from e
            raise

    @staticmethod
    async def get_all_categories(db: AsyncSession, limit: int = 10, offset: int = 0) -> List[CategoryResponse]:
        result = await db.scalars(select(Category).offset(offset).limit(limit))
        return [CategoryResponse.model_validate(c) for c in result.all()]

    @staticmethod
    async def get_category_by_id(db: AsyncSession, category_id: int) -> CategoryResponse:
        category = await db.get(Category, category_id)
        if not category:
            raise CategoryNotFoundError(category_id)
        return CategoryResponse.model_validate(category)

    @staticmethod
    async def update_category(db: AsyncSession, category_id: int, data: CategoryUpdate) -> CategoryResponse:
        try:
            async with db.begin_nested():
                category = await db.get(Category, category_id)
                if not category:
                    raise CategoryNotFoundError(category_id)

                if data.name:
                    name = data.name.strip()
                    await CategoryService._validate_unique(db, name, exclude_id=category_id)
                    category.name = name
                if data.description is not None:
                    category.description = data.description

                await db.flush()  # send UPDATE to DB

            return CategoryResponse.model_validate(category)
        except Exception as e:
            if not isinstance(e, CategoryNotFoundError) and not isinstance(e, DuplicateCategoryError):
                logger.error("update_category error", exc_info=True)
                raise DatabaseError(f"Failed to update category: {e}") from e
            raise

    @staticmethod
    async def delete_category(db: AsyncSession, category_id: int, strict: bool = False) -> None:
        category = await db.get(Category, category_id)
        if not category:
            if strict:
                raise CategoryNotFoundError(category_id)
            return
        try:
            await db.delete(category)
            await db.flush()  # send DELETE to DB
        except Exception as e:
            logger.error("delete_category error", exc_info=True)
            raise DatabaseError(f"Failed to delete category: {e}") from e

    @staticmethod
    async def _validate_unique(db: AsyncSession, name: str, exclude_id: Optional[int] = None) -> None:
        stmt = select(Category).where(Category.name.ilike(name))
        if exclude_id:
            stmt = stmt.where(Category.id != exclude_id)
        result = await db.scalar(stmt)
        if result:
            raise DuplicateCategoryError(name)
