from typing import List
import logging
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import verify_password, get_password_hash
from app.db.models.database_models import User, UserGroup
from app.db.schemas.user_schemas import UserCreate, UserResponse, UserUpdate
from app.core.exceptions import DuplicateResourceException, ResourceNotFoundException, PermissionDeniedException

logger = logging.getLogger(__name__)


class UserService:
    """
    Service Layer for User Management
    Handles user registration, authentication, updates, and group assignments.
    All database operations are wrapped in implicit transactions via the `get_db` dependency.
    """

    @staticmethod
    async def register_user(db: AsyncSession, user_data: UserCreate) -> UserResponse:
        """
        Registers a new user after validating email/username uniqueness.

        Args:
            db: Async database session.
            user_data: User registration details (validated by Pydantic).

        Returns:
            The registered user's details.

        Raises:
            DuplicateResourceException: If the email or username is already taken.
        """
        # Check for existing user with the same email or username
        result = await db.execute(
            select(User).where((User.email == user_data.email) | (User.username == user_data.username))
        )
        existing_user = result.scalar_one_or_none()
        if existing_user:
            # Determine which field caused the conflict
            conflict_field = "email" if existing_user.email == user_data.email else "username"
            raise DuplicateResourceException(
                "User", f"{conflict_field}='{user_data.email if conflict_field == 'email' else user_data.username}'"
            )

        # Create and persist the user
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=get_password_hash(user_data.password),
        )
        db.add(new_user)
        await db.flush()  # Let the transaction context handle the final commit
        logger.info(f"Registered user: {new_user.username} (ID: {new_user.id})")
        return UserResponse.model_validate(new_user)

    @staticmethod
    async def update_user_details(db: AsyncSession, user_id: int, update_data: UserUpdate) -> UserResponse:
        """
        Updates a user's non-sensitive details (full name, email).

        Args:
            db: Async database session.
            user_id: ID of the user to update.
            update_data: Updated user details (validated by Pydantic).

        Returns:
            The updated user's details.

        Raises:
            ResourceNotFoundException: If the user does not exist.
            DuplicateResourceException: If the updated email is already taken.
        """
        user = await UserService._get_user(db, user_id)

        # Validate email uniqueness if updating email
        if update_data.email:
            await UserService._validate_unique_email(db, update_data.email, exclude_id=user_id)

        # Apply updates
        if update_data.full_name:
            user.full_name = update_data.full_name
        if update_data.email:
            user.email = update_data.email

        try:
            await db.flush()  # Ensure constraints are checked
            logger.info(f"Updated user ID {user_id}: {update_data}")
            return UserResponse.model_validate(user)
        except IntegrityError as e:
            await db.rollback()
            raise DuplicateResourceException("User", f"email={update_data.email}") from e

    @staticmethod
    async def change_password(db: AsyncSession, user_id: int, old_password: str, new_password: str) -> None:
        """
        Changes a user's password after verifying the old password.

        Args:
            db: Async database session.
            user_id: ID of the user.
            old_password: Current password for verification.
            new_password: New password to set.

        Raises:
            ResourceNotFoundException: If the user does not exist.
            PermissionDeniedException: If the old password is incorrect.
        """
        user = await UserService._get_user(db, user_id)

        if not verify_password(old_password, user.password_hash):
            raise PermissionDeniedException("Old password is incorrect")

        user.password_hash = get_password_hash(new_password)
        await db.flush()  # Persist changes within the transaction
        logger.info(f"Password updated for user ID {user_id}")

    @staticmethod
    async def authenticate_user(db: AsyncSession, username: str, password: str) -> UserResponse:
        """
        Authenticates a user by verifying credentials.

        Args:
            db: Async database session.
            username: The user's username.
            password: The user's password.

        Returns:
            Authenticated user details.

        Raises:
            ResourceNotFoundException: If the user does not exist.
            PermissionDeniedException: If the password is incorrect.
        """
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()

        if not user:
            raise ResourceNotFoundException("User", username)
        if not verify_password(password, user.password_hash):
            raise PermissionDeniedException("Invalid password")

        return UserResponse.model_validate(user)

    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> UserResponse:
        """
        Retrieves a user by their username.

        Args:
            db: Async database session.
            username: The username to query.

        Returns:
            User details.

        Raises:
            ResourceNotFoundException: If the user does not exist.
        """
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        if not user:
            raise ResourceNotFoundException("User", username)
        return UserResponse.model_validate(user)

    @staticmethod
    async def assign_user_to_group(db: AsyncSession, user_id: int, group_id: int) -> None:
        """
        Assigns a user to a group, ensuring no duplicates.

        Args:
            db: Async database session.
            user_id: ID of the user.
            group_id: ID of the group.

        Raises:
            DuplicateResourceException: If the user is already in the group.
        """
        user_group = UserGroup(user_id=user_id, group_id=group_id)
        try:
            db.add(user_group)
            await db.flush()  # Let the database enforce uniqueness
        except IntegrityError as e:
            await db.rollback()
            raise DuplicateResourceException("UserGroup", f"user_id={user_id}, group_id={group_id}") from e

    @staticmethod
    async def get_user_groups(db: AsyncSession, user_id: int) -> List[int]:
        """
        Retrieves all group IDs associated with a user.

        Args:
            db: Async database session.
            user_id: ID of the user.

        Returns:
            List of group IDs.
        """
        result = await db.execute(select(UserGroup.group_id).where(UserGroup.user_id == user_id))
        return result.scalars().all()

    # ===========================
    # Validation Helpers
    # ===========================
    @staticmethod
    async def _get_user(db: AsyncSession, user_id: int) -> User:
        """
        Internal helper to fetch a user by ID.

        Args:
            db: Async database session.
            user_id: ID of the user.

        Raises:
            ResourceNotFoundException: If the user does not exist.
        """
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise ResourceNotFoundException("User", user_id)
        return user

    @staticmethod
    async def _validate_unique_email(db: AsyncSession, email: str, exclude_id: int = None) -> None:
        """
        Validates email uniqueness during updates.

        Args:
            db: Async database session.
            email: Email to check.
            exclude_id: User ID to exclude from the check (for updates).

        Raises:
            DuplicateResourceException: If the email is already taken.
        """
        stmt = select(User).where(User.email == email)
        if exclude_id:
            stmt = stmt.where(User.id != exclude_id)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise DuplicateResourceException("User", f"email={email}")
