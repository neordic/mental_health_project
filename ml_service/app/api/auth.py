from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from ml_service.app.schemas.auth import UserCreate, UserRead
from ml_service.app.services.auth_service import AuthService
from ml_service.app.db.session import get_db
from ml_service.app.core.security import create_access_token, get_current_user
from ml_service.app.db.models.user import User
from ml_service.app.services.cache_service import get_user_profile_cached, set_user_profile_cached
from ml_service.app.core.logger import get_logger


router = APIRouter()

logger = get_logger("api.auth")

@router.post("/register", response_model=UserRead)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        service = AuthService(db)
        user = service.register_user(user_data)
        logger.info(f"[REGISTER] user_id={user.id} email={user.email}")
        return user
    except Exception as e:
        logger.exception(f"[REGISTER] Failed: email={user_data.email}")
        raise


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        service = AuthService(db)
        login_data = service.authenticate_user(
            email=form_data.username,
            password=form_data.password
        )
        token = create_access_token({"sub": login_data.id})
        logger.info(f"[LOGIN] user_id={login_data.id} email={login_data.email}")
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        logger.warning(f"[LOGIN] Failed attempt email={form_data.username}")
        raise



@router.get("/me", response_model=UserRead)
def get_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        
        cached = get_user_profile_cached(current_user.id)
        if cached:
            logger.info(f"[ME] Cache HIT for user_id={current_user.id}")
            return cached

        
        logger.info(f"[ME] Cache MISS for user_id={current_user.id}")
        profile = UserRead.from_orm(current_user)
        set_user_profile_cached(current_user.id, profile)
        return profile
    except Exception:
        logger.exception(f"[ME] Failed to fetch profile for user_id={current_user.id}")
        raise


