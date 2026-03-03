from sqlalchemy import or_
from app.core.redis import redis
from app.core.celery import celery
from app.db.session import SessionLocal
from app.db.models.link import Link
from datetime import datetime, timedelta


@celery.task
def delete_rotten_links():
    db = SessionLocal()
    lifetime = timedelta(days=30)
    timeline = datetime.now() - lifetime
    rotten_links = db.query(Link).filter(or_(Link.expires_at < datetime.now(), Link.date_last_click < timeline)).all()
    for link in rotten_links:
        db.delete(link)
    db.commit()
    for link in rotten_links:
        redis.delete(f"link:{link.short_code}")
    db.close()  