from sqlalchemy import Column, Integer, BigInteger, String, DateTime
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now)