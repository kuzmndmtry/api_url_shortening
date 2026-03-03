import datetime

from app.core.redis import redis
from app.db.models.link import Link
from fastapi import HTTPException
from app.db.models.user import User
from app.schemas.link import LinkCreate
from app.services.link_service import create_short_code, generate_short_code, get_link, get_statistics
from fastapi import APIRouter
from fastapi import Depends, Header
from sqlalchemy.orm import Session
from app.db.session import get_db
from typing import Optional


router = APIRouter()

@router.post("/shorten") # создание + уникальный элиас
def shorten_url(
    link: LinkCreate,
    db: Session = Depends(get_db), 
    current_user: Optional[int] = Header(default=None, alias="User-ID")
    ):
    if current_user:
        user = db.query(User).filter_by(id=current_user).first()
        if user is None:
            raise HTTPException(status_code=401, detail="invalid user")
    else:
        user = None
    short_code = create_short_code(db, link.original_url, owner_id=user.id if user else None, alias=link.custom_alias, expires_at=link.expires_at)
    return {"short_code": short_code}

@router.get("/search") # поиск по ориг урл
def search_links(
    original_url: str,
    db: Session = Depends(get_db), 
    current_user: int = Header(alias="X-User-ID")
    ):
    if not current_user:
        raise HTTPException(status_code=401, detail="unauthorized")
    link = get_link(db, original_url, current_user)
    if link is None:
        raise HTTPException(status_code=404, detail="not found")
    return link

@router.get("/{short_code}/stats") # статистика
def link_statistics(
    short_code: str,
    db: Session = Depends(get_db)):
    stats = get_statistics(db, short_code)
    if stats is None:
        raise HTTPException(status_code=404, detail="not found")
    return stats

@router.put("/{short_code}") # изменение 
def update_short_code(
    short_code: str, 
    db: Session = Depends(get_db), 
    current_user: int = Header(alias="X-User-ID")
    ):
    if not current_user:
        raise HTTPException(status_code=401, detail="unauthorized")
    link = db.query(Link).filter_by(short_code=short_code).first()
    if link is None:
        raise HTTPException(status_code=404, detail="not found")
    if link.owner_id != current_user:
        raise HTTPException(status_code=403, detail="access denied")
    new_short_code = generate_short_code(db)
    link.short_code = new_short_code
    db.commit()
    db.refresh(link)

    redis.delete(f"link:{short_code}")
    return {"short_code": link.short_code}

@router.delete("/{short_code}") # удаление
def delete_short_code(
    short_code: str, 
    db: Session = Depends(get_db), 
    current_user: int = Header(alias="X-User-ID")
    ):
    if not current_user:
        raise HTTPException(status_code=401, detail="unauthorized")
    link = db.query(Link).filter_by(short_code=short_code).first()
    if link is None:
        raise HTTPException(status_code=404, detail="not found")
    if link.owner_id != current_user:
        raise HTTPException(status_code=403, detail="access denied")
    db.delete(link)
    db.commit()
    redis.delete(f"link:{short_code}")   
    return {"detail": "success!"}

@router.get("/{short_code}") # клик
def redirect_to_original(
    short_code: str, 
    db: Session = Depends(get_db)
    ):
    cach_link = redis.get(f"link:{short_code}")
    if cach_link:
        link = db.query(Link).filter_by(short_code=short_code).first()
        link.count_clicks += 1
        db.commit()
        return {"original_url": cach_link}
    link = db.query(Link).filter_by(short_code=short_code).first()
    if link is None:
        raise HTTPException(status_code=404, detail="not found")
    redis.set(f"link:{short_code}", link.original_url, ex = 60)
    link.count_clicks += 1
    link.date_last_click = datetime.datetime.now()
    db.commit()
    return {"original_url": link.original_url}






