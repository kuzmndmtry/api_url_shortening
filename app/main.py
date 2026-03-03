from fastapi import FastAPI
from app.api.routes import auth,links
from app.db.base import Base
from app.db.session import engine

app = FastAPI(title="URL shortening")

# Base.metadata.create_all(bind=engine)


app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(links.router, prefix="/links", tags=["Links"])
