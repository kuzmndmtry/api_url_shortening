import datetime 
import random
import string
from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.models.link import Link

def generate_short_code(db: Session):
    length = 6
    characters = string.ascii_letters + string.digits
    while True:
        short_code = ''.join(random.choice(characters) for _ in range(length))
        exist = db.query(Link).filter_by(short_code=short_code).first()
        if not exist:
            return short_code
        
def chek_alias(db: Session, alias: str) -> bool:
   return db.query(Link).filter_by(short_code=alias).first() is not None

def create_short_code(db: Session,
                     original_url: str, 
                     owner_id: Optional[int] = None,
                     alias: Optional[str] = None,
                     expires_at:Optional[datetime.datetime] = None 
                     ):
    if alias:
        if chek_alias(db,alias):
            raise HTTPException(status_code = 400, detail='alias alredy exists')
        else:
            short_code = alias
    else:
        short_code = generate_short_code(db)
    if owner_id is None and expires_at is None:
        expires_at = datetime.datetime.now() + datetime.timedelta(days=30)
    link = Link(original_url=str(original_url), short_code=short_code, owner_id=owner_id, expires_at = expires_at)
    db.add(link)
    try:
        db.commit()
        db.refresh(link)
        return link.short_code
    except Exception as e:
        db.rollback()
        raise e
    
def get_statistics(db: Session, short_code: str):
    link = db.query(Link).filter_by(short_code=short_code).first()
    if link is None:
        return None
    return {
        "original_url": link.original_url,
        "created_date": link.created_date,
        "count_clicks": link.count_clicks,
        "date_last_click": link.date_last_click
    }

def get_link(db: Session, original_url: str, owner_id: int ):
    link = db.query(Link).filter(
        Link.original_url==original_url,
        Link.owner_id==owner_id).first()
    if link is None:
        return None
    return {
        "original_url": link.original_url,
        "short_code": link.short_code,
        "created_date": link.created_date,
        "count_clicks": link.count_clicks,
        "date_last_click": link.date_last_click
    }

    