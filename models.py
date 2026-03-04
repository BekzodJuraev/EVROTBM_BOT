from sqlalchemy import Column, Integer, BigInteger, String, DateTime,Enum
from datetime import datetime
from database import Base
import enum
class OrderStatus(enum.Enum):
    PENDING = "pending"
    CALCULATION = "calculation"
    SENDING = "sending"
    READY = "ready"
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now)


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger)
    message_id = Column(BigInteger)
    order_text = Column(String)

    # Используем Enum для контроля статусов
    status = Column(
        Enum(OrderStatus),
        default=OrderStatus.PENDING,
        server_default=OrderStatus.PENDING.value
    )

    created_at = Column(DateTime, default=datetime.now)