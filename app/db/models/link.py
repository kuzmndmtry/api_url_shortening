from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
class Link(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    original_url = Column(String, nullable=False)
    short_code = Column(String, unique=True, index=True, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime, nullable=True)
    count_clicks = Column(Integer, default=0)
    date_last_click = Column(DateTime(timezone=True), nullable=True)
    
    owner = relationship("User", back_populates="links")