from typing import Optional, List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.security import verify_password, get_password_hash
from app.db.models.database_models import User, UserGroup
from app.db.schemas.user_schemas import UserCreate, UserResponse, UserUpdate
from app.core.exceptions import DuplicateResourceException, ResourceNotFoundException


class UserService:
    """
    Service Layer for User Management
    Handles all user-related database operations:
    - Secure password hashing & authentication.
    - User creation, retrieval, and updates.
    - Managing user-group assignments.
    """

    @staticmethod
    async def register_user(db: AsyncSession, user_data: UserCreate) -> UserResponse:
        """
        Registers a new user with hashed password.
        Ensures email and username uniqueness.

        Args:
            db (AsyncSession): The database AsyncSession.
            user_data (UserCreate): User registration details.

        Returns:
            UserResponse: The created user's details.

        Raises:
            DuplicateResourceException: If the email or username already exists.
        """
        # Check for duplicate email or username
        result = await db.execute(
            select(User).where((User.email == user_data.email) | (User.username == user_data.username))
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise DuplicateResourceException("User", user_data.username)

        # Create new user
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=get_password_hash(user_data.password),
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return UserResponse.model_validate(new_user)

    @staticmethod
    async def update_user_details(db: AsyncSession, user_id: int, update_data: UserUpdate) -> UserResponse:
        """
        Updates a user's details (excluding password).

        Args:
            db (AsyncSession): The database AsyncSession.
            user_id (int): The ID of the user to update.
            update_data (UserUpdate): Updated user details.

        Returns:
            UserResponse: The updated user's details.

        Raises:
            ResourceNotFoundException: If the user does not exist.
        """
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise ResourceNotFoundException("User", user_id)

        # Update non-password fields
        user.full_name = update_data.full_name or user.full_name
        user.email = update_data.email or user.email

        await db.commit()
        await db.refresh(user)

        return UserResponse.model_validate(user)

    @staticmethod
    async def change_password(db: AsyncSession, user_id: int, old_password: str, new_password: str) -> bool:
        """
        Changes a user's password after validating the old password.

        Args:
            db (AsyncSession): The database AsyncSession.
            user_id (int): The ID of the user.
            old_password (str): The current password.
            new_password (str): The new password.

        Returns:
            bool: True if the password was successfully updated.

        Raises:
            ResourceNotFoundException: If the user does not exist.
            HTTPException: If the old password is incorrect.
        """
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise ResourceNotFoundException("User", user_id)

        # Validate old password
        if not verify_password(old_password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Old password is incorrect")

        # Update password
        user.password_hash = get_password_hash(new_password)
        await db.commit()

        return True

    @staticmethod
    async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[UserResponse]:
        """
        Authenticates a user by verifying their credentials.

        Args:
            db (AsyncSession): The database AsyncSession.
            username (str): The user's username.
            password (str): The user's password.

        Returns:
            Optional[UserResponse]: The authenticated user's details, or None if invalid.

        Raises:
            HTTPException: If the credentials are invalid.
        """
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()

        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

        return UserResponse.model_validate(user)

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> UserResponse:
        """
        Retrieves a user by their ID.

        Args:
            db (AsyncSession): The database AsyncSession.
            user_id (int): The ID of the user.

        Returns:
            UserResponse: The requested user's details.

        Raises:
            ResourceNotFoundException: If the user does not exist.
        """
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise ResourceNotFoundException("User", user_id)

        return UserResponse.model_validate(user)

    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> UserResponse:
        """
        Retrieves a user by their username.

        Args:
            db (AsyncSession): The database AsyncSession.
            username (str): The username of the user.

        Returns:
            UserResponse: The requested user's details.

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
        Assigns a user to a group.
        Ensures no duplicate assignments.

        Args:
            db (AsyncSession): The database AsyncSession.
            user_id (int): The ID of the user.
            group_id (int): The ID of the group.

        Raises:
            HTTPException: If an error occurs during assignment.
        """
        try:
            result = await db.execute(
                select(UserGroup).where(UserGroup.user_id == user_id, UserGroup.group_id == group_id)
            )
            existing_assignment = result.scalar_one_or_none()

            if not existing_assignment:
                user_group = UserGroup(user_id=user_id, group_id=group_id)
                db.add(user_group)
                await db.commit()
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    @staticmethod
    async def get_user_groups(db: AsyncSession, user_id: int) -> List[int]:
        """
        Retrieves all group IDs for a given user.

        Args:
            db (AsyncSession): The database session.
            user_id (int): The ID of the user.

        Returns:
            List[int]: A list of group IDs the user belongs to.
        """
        result = await db.execute(select(UserGroup.group_id).where(UserGroup.user_id == user_id))
        groups = result.scalars().all()

        return list(groups)
