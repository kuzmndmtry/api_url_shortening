from app.db.models.user import User
from sqlalchemy.orm import Session
from fastapi import HTTPException


def create_user(db: Session, username: str, password: str):
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    user = User(username=username, password=password)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user