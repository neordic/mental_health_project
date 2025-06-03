from ml_service.app.db.session import Base, get_db, settings
from ml_service.app.db.session import engine
from ml_service.app.db.models import user, user_credits, inference_task, billing_record

print("Создание таблиц...")
print(settings.dict())  

Base.metadata.create_all(bind=engine)
print("Готово.")