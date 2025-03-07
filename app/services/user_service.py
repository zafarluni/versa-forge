from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.security import verify_password, get_password_hash
from app.db.models.database_models import User, UserGroup
from app.db.schemas.user_schemas import UserCreate, UserResponse
from app.core.exceptions import DuplicateResourceException, ResourceNotFoundException


class UserService:
    """
    Handles all user-related database operations.
    - Secure password hashing & authentication.
    - User creation and retrieval.
    - Managing user-group assignments.
    """

    @staticmethod
    def register_user(db: Session, user_data: UserCreate) -> UserResponse:
        """
        Creates a new user with hashed password.
        Ensures email uniqueness.
        """
        existing_user = db.execute(select(User).where(User.email == user_data.email)).scalar_one_or_none()

        if existing_user:
            raise DuplicateResourceException("User", user_data.email)

        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=get_password_hash(user_data.password),
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return UserResponse.model_validate(new_user)

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[UserResponse]:
        """
        Validates user credentials and returns the user if authenticated.
        """
        user = db.execute(select(User).where(User.username == username)).scalar_one_or_none()

        if not user or not verify_password(password, str(user.password_hash)):
            return None  # Invalid credentials

        return UserResponse.model_validate(user)

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> UserResponse:
        """
        Retrieves a user by ID.
        """
        user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()

        if not user:
            raise ResourceNotFoundException("User", user_id)

        return UserResponse.model_validate(user)

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> UserResponse:
        """
        Retrieves a user by username.
        """
        user = db.execute(select(User).where(User.username == username)).scalar_one_or_none()

        if not user:
            raise ResourceNotFoundException("User", 1)

        return UserResponse.model_validate(user)

    @staticmethod
    def assign_user_to_group(db: Session, user_id: int, group_id: int) -> None:
        """
        Assigns a user to a group.
        - Ensures no duplicate assignments.
        """
        existing_assignment = db.execute(
            select(UserGroup).where(UserGroup.user_id == user_id, UserGroup.group_id == group_id)
        ).scalar_one_or_none()

        if not existing_assignment:
            user_group = UserGroup(user_id=user_id, group_id=group_id)
            db.add(user_group)
            db.commit()

    @staticmethod
    def get_user_groups(db: Session, user_id: int) -> List[int]:
        """
        Retrieves all group IDs for a given user.
        """
        stmt = select(UserGroup.group_id).where(UserGroup.user_id == user_id)
        groups = db.execute(stmt).scalars().all()

        return list(groups)
