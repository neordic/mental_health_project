from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from ml_service.app.schemas.auth import UserCreate
from ml_service.app.repositories.user_repo import UserRepository
from ml_service.app.services.billing_service import BillingService  
from ml_service.app.services.cache_service import set_user_profile_cached 
from ml_service.app.db.models.user import User
from ml_service.app.core.logger import get_logger
from sqlalchemy.exc import IntegrityError 

logger = get_logger("auth")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)
        self.billing = BillingService(db) 

    def register_user(self, user_data: UserCreate) -> User:
        existing_user = self.repo.get_by_email(user_data.email)
        if existing_user:
            logger.warning(f"[AUTH] Attempt to register existing user: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )

        hashed_password = pwd_context.hash(user_data.password)

        try:
            user = self.repo.create(user_data, hashed_password)
        except IntegrityError as e:
            logger.warning(f"[AUTH] Integrity error on user creation: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with that name already exists"
            )

        logger.info(f"[AUTH] New user registered: {user.email} (id={user.id})")

        # Начисляем кредиты при регистрации
        self.billing.credit_user(user.id, amount=10)

        # Сохраняем профиль в кэше
        set_user_profile_cached(user.id, {
            "id": user.id,
            "username": user.username,
            "email": user.email
        })

        logger.info(f"[AUTH] User profile cached for user_id={user.id}")
        return user

    def authenticate_user(self, email: str, password: str) -> User:
        user = self.repo.get_by_email(email)
        if not user or not pwd_context.verify(password, user.password_hash):
            logger.warning(f"[AUTH] Failed login for {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        logger.info(f"[AUTH] Login success for user_id={user.id}")
        return user
