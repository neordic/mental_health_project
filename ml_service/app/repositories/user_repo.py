from sqlalchemy.orm import Session
from ml_service.app.db.models.user import User
from ml_service.app.schemas.auth import UserCreate

from ml_service.app.core.logger import get_logger  

logger = get_logger("user_repo")

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        logger.info(f" Поиск пользователя по email: {email}")
        return self.db.query(User).filter(User.email == email).first()

    def create(self, user_create: UserCreate, hashed_password: str) -> User:
        logger.info(f" Создание пользователя: {user_create.email}")
        user = User(
            username=user_create.username,
            email=user_create.email,
            password_hash=hashed_password
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        logger.info(f" Пользователь создан: id={user.id}, email={user.email}")
        return user

    def get_by_id(self, user_id: int) -> User | None:
        logger.info(f" Поиск пользователя по ID: {user_id}")
        return self.db.query(User).filter(User.id == user_id).first()
    def get_by_username(self, username: str) -> User | None:
        logger.info(f" Поиск пользователя по username: {username}")
        return self.db.query(User).filter(User.username == username).first()

