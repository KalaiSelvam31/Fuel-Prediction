from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..schemas import UserCreate, UserResponse, Token
from ..crud import create_user, get_user_by_email, get_user_by_username, authenticate_user
from ..database import get_db
from ..auth import create_access_token

router = APIRouter()


@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if email already exists
    if get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check if username already exists
    if get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already taken")

    # Create new user
    db_user = create_user(db, user)
    return db_user


@router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Authenticate user
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token, token_type="bearer")