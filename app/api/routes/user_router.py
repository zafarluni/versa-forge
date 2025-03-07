from datetime import timedelta
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import jwt

from app.db.database import get_db
from app.db.schemas.token_schema import TokenData
from app.db.schemas.user_schemas import UserCreate, UserResponse
from app.services.user_service import UserService
from app.core.security import create_jwt_token, get_jwt_payload
from app.utils.config import settings

router = APIRouter(prefix="/users", tags=["Users"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")


# ===========================
# 2️⃣ User Login (Issue JWT)
# ===========================
@router.post("/login", response_model=Dict[str, str])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> Dict[str, str]:
    """
    Authenticate user and return a JWT token.

    Args:
        form_data (OAuth2PasswordRequestForm): Login credentials (username=email, password).
        db (Session): Database session.

    Returns:
        Dict[str, str]: Access token and token type.
    """
    user = UserService.authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Token data to store in JWT
    token_data = TokenData(
        id=int(user.id),
        username=str(user.username),
        full_name=str(user.full_name),
        email=str(user.email),
        is_active=bool(user.is_active),
    )
    # Create JWT token
    token = create_jwt_token(token_data=token_data, expires_delta=timedelta(minutes=60))

    return {"access_token": token, "token_type": "bearer"}


# ===========================
#  Verify JWT & Get User Info
# ===========================
@router.get("/me", response_model=TokenData)
def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """
    Get the currently authenticated user from JWT.

    Args:
        token (str): JWT token from request.

    Returns:
        Dict[str, str]: User ID and email.
    """
    try:
        return get_jwt_payload(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ===========================
# Get User Details
# ===========================
@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)) -> UserResponse:
    """
    Retrieve user details by ID.

    Args:
        user_id (int): ID of the user.
        db (Session): Database session.

    Returns:
        UserResponse: User details.
    """
    return UserService.get_user_by_id(db, user_id)


# ===========================
# 3️⃣ User Registration
# ===========================
# @router.post("/register", response_model=UserResponse)
# def register(user_data: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
#     """
#     Register a new user.

#     Args:
#         user_data (UserCreate): User registration details.
#         db (Session): Database session.

#     Returns:
#         UserResponse: Registered user details.
#     """
#     return UserService.register_user(db, user_data)


# ===========================
# 5️⃣ Assign User to a Group
# ===========================
# @router.post("/{user_id}/groups/{group_id}", response_model=Dict[str, str])
# def assign_user_to_group(user_id: int, group_id: int, db: Session = Depends(get_db)) -> Dict[str, str]:
#     """
#     Assign a user to a group.

#     Args:
#         user_id (int): ID of the user.
#         group_id (int): ID of the group.
#         db (Session): Database session.

#     Returns:
#         Dict[str, str]: Success message.
#     """
#     UserService.assign_user_to_group(db, user_id, group_id)
#     return {"message": f"User {user_id} assigned to group {group_id}"}


# ===========================
# 6️⃣ Get All Groups for a User
# ===========================
@router.get("/{user_id}/groups", response_model=List[int])
def get_user_groups(user_id: int, db: Session = Depends(get_db)) -> List[int]:
    """
    Retrieve all groups a user belongs to.

    Args:
        user_id (int): ID of the user.
        db (Session): Database session.

    Returns:
        List[int]: List of group IDs the user is assigned to.
    """
    return UserService.get_user_groups(db, user_id)
