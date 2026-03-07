from pydantic import BaseModel, field_validator
from datetime import datetime, date
import re

class DateValidation(BaseModel):
    input_date: str

    # @field_validator("input_date")
    # @classmethod
    # def validate_ready_date(cls, v: str) -> date:
    #     # 1. Пытаемся превратить строку в объект даты
    #     try:
    #         # Ожидаем формат День.Месяц.Год (например, 05.03.2026)
    #         parsed_date = datetime.strptime(v, "%d.%m.%Y").date()
    #     except ValueError:
    #         raise ValueError("Неверный формат! Используйте ДД.ММ.ГГГГ (например, 15.05.2024)")
    #
    #     # 2. Проверяем, чтобы дата не была в прошлом
    #     if parsed_date < date.today():
    #         raise ValueError("Дата не может быть в прошлом!")
    #
    #     return parsed_date



class UserContact(BaseModel):
    phone: str

    # @field_validator("phone")
    # @classmethod
    # def validate_phone(cls, v):
    #     # Регулярка для Узбекистана: +998XXXXXXXXX
    #     pattern = r"^\+998\d{9}$"
    #     if not re.match(pattern, v):
    #         raise ValueError("Формат телефона должен быть +998XXXXXXXXX")
    #     return v