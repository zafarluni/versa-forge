from fastapi import APIRouter, Depends, HTTPException, Security, Header
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timezone, timedelta
from app.utils.config import settings
from app.core.security import authenticate_user, create_access_token 

from app.db.schemas.token_schema import Token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Handles user login and generates a JWT token upon successful authentication.

    Args:
        form_data (OAuth2PasswordRequestForm): The form data containing the user's credentials.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

