"""
Category Service Module

Author: Zafar Hussain Luni
Version: 2.0.0
"""

import logging
from typing import List
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.database_models import Category
from app.db.schemas.category_schemas import CategoryCreate, CategoryResponse, CategoryUpdate
from app.core.exceptions import CategoryNotFoundException, DuplicateCategoryException

logger = logging.getLogger(__name__)


class CategoryService:
    """
    Service layer for category management operations.
    All database operations are wrapped in transactions managed by the session context.
    """

    # ===========================
    # CRUD Operations
    # ===========================

    @staticmethod
    async def create_category(db: AsyncSession, category_data: CategoryCreate) -> CategoryResponse:
        """
        Create a new category with validation.
        - Ensures unique category name.
        - Uses flush() to generate ID without committing the transaction.
        """
        await CategoryService._validate_unique_category(db, category_data.name.strip())

        new_category = Category(name=category_data.name.strip(), description=category_data.description)

        try:
            db.add(new_category)
            await db.flush()  # Ensure ID generation without committing
            logger.info(f"Created category: {new_category.name} (ID: {new_category.id})")
            return CategoryResponse.model_validate(new_category)

        except Exception as e:
            logger.error(f"Unexpected error during category update: {str(e)}", exc_info=True)
            raise

    @staticmethod
    async def get_all_categories(db: AsyncSession, limit: int = 10, offset: int = 0) -> List[CategoryResponse]:
        """
        Retrieve paginated list of categories.
        - Read-only operation within an implicit transaction.
        """
        result = await db.execute(select(Category).offset(offset).limit(limit))
        categories = result.scalars().all()
        return [CategoryResponse.model_validate(c) for c in categories]

    @staticmethod
    async def get_category_by_id(db: AsyncSession, category_id: int) -> CategoryResponse:
        """
        Get single category by ID with validation.
        - Raises CategoryNotFoundException if the category does not exist.
        """
        category = await CategoryService._get_category(db, category_id)
        return CategoryResponse.model_validate(category)

    @staticmethod
    async def update_category(db: AsyncSession, category_id: int, update_data: CategoryUpdate) -> CategoryResponse:
        """
        Update category details with validation.
        - Ensures unique category name if provided.
        - Uses flush() to apply changes without committing the transaction.
        """
        category = await CategoryService._get_category(db, category_id)

        if update_data.name:
            await CategoryService._validate_unique_category(db, update_data.name.strip(), exclude_id=category_id)

        update_values = {
            "name": update_data.name.strip() if update_data.name else category.name,
            "description": update_data.description or category.description,
        }

        try:
            await db.execute(update(Category).where(Category.id == category_id).values(**update_values))
            await db.refresh(category)  # Refresh to reflect updated values in the session
            logger.info(f"Updated category: {category.name} (ID: {category.id})")
            return CategoryResponse.model_validate(category)

        except Exception as e:
            logger.error(f"Unexpected error during category update: {str(e)}", exc_info=True)
            raise

    @staticmethod
    async def delete_category(db: AsyncSession, category_id: int, strict: bool = False) -> None:
        """
        Delete category with existence validation.
        - If strict mode is enabled, raises CategoryNotFoundException if the category does not exist.
        - Otherwise, ignores deletion for non-existent categories.
        """
        category = await db.get(Category, category_id)

        if not category:
            if strict:
                logger.warning(f"Category not found (strict mode): ID {category_id}")
                raise CategoryNotFoundException(category_id)
            logger.info(f"Ignoring delete for non-existent category: ID {category_id}")
            return

        try:
            await db.delete(category)
            logger.info(f"Deleted category: {category.name} (ID: {category.id})")

        except Exception as e:
            logger.error(f"Error during category deletion: {str(e)}", exc_info=True)
            raise

    # ===========================
    # Validation Helpers
    # ===========================

    @staticmethod
    async def _validate_unique_category(db: AsyncSession, name: str, exclude_id: int | None = None) -> None:
        """
        Validate category name uniqueness.
        - Raises DuplicateCategoryException if a duplicate category exists.
        """
        stmt = select(Category).where(Category.name.ilike(name.strip()))
        if exclude_id:
            stmt = stmt.where(Category.id != exclude_id)

        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            logger.warning(f"Duplicate category attempt: {name}")
            raise DuplicateCategoryException(name)

    @staticmethod
    async def _get_category(db: AsyncSession, category_id: int) -> Category:
        """
        Internal method to get category or raise exception.
        - Raises CategoryNotFoundException if the category does not exist.
        """
        category = await db.get(Category, category_id)
        if not category:
            logger.warning(f"Category not found: ID {category_id}")
            raise CategoryNotFoundException(category_id)
        return category
