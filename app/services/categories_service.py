"""
Category Service Module

This module provides business logic for managing categories,
including creation, retrieval, and deletion operations.

Best Practices:
- Uses structured logging for monitoring.
- Ensures exception handling for business errors.
- Avoids redundant database queries.

Author: Zafar Hussain Luni
Version: 1.0.0
"""

import logging
from typing import List
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.database_models import Category
from app.db.schemas.category_schemas import CategoryCreate, CategoryResponse
from app.core.exceptions import CategoryNotFoundException, DuplicateCategoryException

# Configure logger for this module
logger = logging.getLogger(__name__)


class CategoryService:
    """
    Service class for managing categories.
    """

    @staticmethod
    def create_category(db: Session, category_data: CategoryCreate) -> CategoryResponse:
        """
        Creates a new category if it doesn't already exist.

        Args:
            db (Session): The database session.
            category_data (CategoryCreate): The category data.

        Returns:
            CategoryResponse: The created category.

        Raises:
            DuplicateCategoryException: If the category already exists.
        """
        stmt = select(Category).where(Category.name.ilike(category_data.name.strip()))
        existing_category = db.execute(stmt).scalar_one_or_none()

        if existing_category:
            logger.warning("Duplicate category creation attempt: %s", category_data.name)
            raise DuplicateCategoryException(category_data.name)

        new_category = Category(name=category_data.name.strip(), description=category_data.description)
        try:
            db.add(new_category)
            db.commit()
            db.refresh(new_category)
            logger.info("Created category: %s (ID: %d)", new_category.name, new_category.id)
            return CategoryResponse.model_validate(new_category)
        except Exception as e:
            db.rollback()  # Ensure rollback on failure
            logger.error("Failed to create category: %s - %s", category_data.name, str(e), exc_info=True)
            raise

    @staticmethod
    def get_all_categories(db: Session, limit: int = 10, offset: int = 0) -> List[CategoryResponse]:
        """
        Retrieves all categories.

        Args:
            db (Session): The database session.

        Returns:
            List[CategoryResponse]: A list of all categories.
        """
        stmt = select(Category).offset(offset).limit(limit)
        categories = db.execute(stmt).scalars().all()
        logger.info("Retrieved %d categories", len(categories))
        return [CategoryResponse.model_validate(category) for category in categories]

    @staticmethod
    def get_category_by_id(db: Session, category_id: int) -> CategoryResponse:
        """
        Retrieves a category by its ID.

        Args:
            db (Session): The database session.
            category_id (int): The ID of the category.

        Returns:
            CategoryResponse: The requested category.

        Raises:
            CategoryNotFoundException: If the category is not found.
        """
        category = CategoryService._get_category_or_raise(db, category_id)
        logger.info("Retrieved category: %s (ID: %d)", category.name, category.id)
        return CategoryResponse.model_validate(category)

    @staticmethod
    def delete_category(db: Session, category_id: int, strict: bool = False) -> None:
        """
        Deletes a category by its ID.

        Args:
            db (Session): The database session.
            category_id (int): The ID of the category.
            strict (bool): Whether to enforce strict deletion (404 if not found).

        Returns:
            None
        """
        stmt = select(Category).where(Category.id == category_id)
        category = db.execute(stmt).scalar_one_or_none()

        if not category:
            if strict:
                logger.warning("Category not found (strict mode): ID %d", category_id)
                raise CategoryNotFoundException(category_id)
            logger.info("Category not found (non-strict mode), ignoring: ID %d", category_id)
            return  # Non-strict mode allows returning 204

        try:
            db.delete(category)
            db.commit()
            logger.info("Deleted category: %s (ID: %d)", category.name, category.id)
        except Exception as e:
            db.rollback()
            logger.error("Failed to delete category: %s (ID: %d) - %s", category.name, category.id, str(e), exc_info=True)
            raise

    @staticmethod
    def _get_category_or_raise(db: Session, category_id: int) -> Category:
        """
        Private method to fetch a category by ID or raise an exception.

        Args:
            db (Session): The database session.
            category_id (int): The category ID.

        Returns:
            Category: The fetched category.

        Raises:
            CategoryNotFoundException: If the category does not exist.
        """
        stmt = select(Category).where(Category.id == category_id)
        category = db.execute(stmt).scalar_one_or_none()

        if not category:
            logger.warning("Category not found: ID %d", category_id)
            raise CategoryNotFoundException(category_id)

        return category
