from app.db.base import Base
from app.db.session import engine
from app.db.models import User, Link


def init_db():
    Base.metadata.create_all(bind=engine)