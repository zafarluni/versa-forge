import logging
from typing import List

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    DatabaseError,
    DuplicateResourceError,
    PermissionDeniedError,
    ResourceNotFoundError,
)
from app.core.security import get_password_hash, verify_password
from app.db.models.database_models import Group, User, UserGroup
from app.schemas.user_schemas import (
    UserCreate,
    UserResponse,
    UserUpdate,
)

logger = logging.getLogger(__name__)


class UserService:
    @staticmethod
    async def register_user(db: AsyncSession, user_data: UserCreate) -> UserResponse:
        """
        Registers a new user after validating email/username uniqueness.
        """
        existing = await db.scalar(
            select(User).where((User.email == user_data.email) | (User.username == user_data.username))
        )
        if existing:
            field = "email" if existing.email == user_data.email else "username"
            raise DuplicateResourceError("User", f"{field} already taken")

        user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=get_password_hash(user_data.password),
            full_name=user_data.full_name,
        )
        try:
            db.add(user)
            await db.flush()
            await db.refresh(user)
            return UserResponse.model_validate(user)
        except IntegrityError as e:
            logger.exception("Integrity error on user registration")
            raise DuplicateResourceError("User", "Email or username already taken") from e
        except Exception as e:
            logger.exception("Unknown error on user registration")
            raise DatabaseError("Failed to register user") from e

    @staticmethod
    async def update_user_details(db: AsyncSession, user_id: int, data: UserUpdate) -> UserResponse:
        """
        Updates full_name and/or email for a user.
        """
        user = await db.get(User, user_id)
        if not user:
            raise ResourceNotFoundError("User", user_id)

        if data.email and data.email != user.email:
            exists = await db.scalar(select(User).where(User.email == data.email, User.id != user_id))
            if exists:
                raise DuplicateResourceError("User", "email already taken")
            user.email = data.email

        if data.full_name is not None:
            user.full_name = data.full_name

        try:
            await db.flush()
            await db.refresh(user)
            return UserResponse.model_validate(user)
        except IntegrityError as e:
            logger.exception("Integrity error on user update")
            raise DatabaseError(f"Failed to update user: {e}") from e

    @staticmethod
    async def change_password(db: AsyncSession, user_id: int, old_password: str, new_password: str) -> None:
        """
        Verifies old_password then updates to new_password.
        """
        user = await db.get(User, user_id)
        if not user:
            raise ResourceNotFoundError("User", user_id)

        if not verify_password(old_password, user.password_hash):
            raise PermissionDeniedError("Old password incorrect")

        user.password_hash = get_password_hash(new_password)
        try:
            await db.flush()
        except Exception as e:
            logger.exception("Failed to change password")
            raise DatabaseError(f"Failed to change password: {e}") from e

    @staticmethod
    async def authenticate_user(db: AsyncSession, username: str, password: str) -> UserResponse:
        """
        Fetches user by username and verifies password.
        """
        user = await db.scalar(select(User).where(User.username == username))
        if not user or not verify_password(password, user.password_hash):
            import asyncio

            await asyncio.sleep(0.1)
            raise PermissionDeniedError("Invalid credentials")

        if not user.is_active:
            raise PermissionDeniedError("Account is inactive")

        return UserResponse.model_validate(user)

    @staticmethod
    async def get_user_groups(db: AsyncSession, user_id: int) -> List[int]:
        """
        Returns IDs of groups the user belongs to.
        """
        result = await db.scalars(select(UserGroup.group_id).where(UserGroup.user_id == user_id))
        return list(result.all())

    @staticmethod
    async def assign_user_to_group(db: AsyncSession, user_id: int, group_id: int) -> None:
        """
        Creates a UserGroup mapping, enforcing uniqueness and existence.
        """
        user = await db.get(User, user_id)
        if not user:
            raise ResourceNotFoundError("User", user_id)
        group = await db.get(Group, group_id)
        if not group:
            raise ResourceNotFoundError("Group", group_id)

        ug = UserGroup(user_id=user_id, group_id=group_id)
        try:
            db.add(ug)
            await db.flush()
        except IntegrityError as e:
            logger.exception("Integrity error on user-group assignment")
            raise DuplicateResourceError("UserGroup", f"user_id={user_id}, group_id={group_id}") from e

    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> UserResponse:
        """
        Retrieves a single user by username.
        """
        if not username or not isinstance(username, str):
            raise ValueError("Username must be a non-empty string")

        user = await db.scalar(select(User).where(User.username == username))
        if not user:
            raise ResourceNotFoundError("User", username)
        return UserResponse.model_validate(user)
