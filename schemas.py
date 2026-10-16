"""Pydantic models: validate incoming API data and shape outgoing responses."""
import re
from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class StudentBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    date_of_birth: date
    email: Optional[str] = Field(default=None, max_length=254)
    phone: Optional[str] = Field(default=None, max_length=30)
    course: Optional[str] = Field(default=None, max_length=100)
    address: Optional[str] = Field(default=None, max_length=250)
    enrollment_date: Optional[date] = None

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Name cannot be blank")
        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: Optional[str]) -> Optional[str]:
        if value is None or value.strip() == "":
            return None
        value = value.strip().lower()
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
            raise ValueError("Enter a valid email address")
        return value

    @field_validator("phone")
    @classmethod
    def clean_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is None or value.strip() == "":
            return None
        return value.strip()


class StudentCreate(StudentBase):
    @model_validator(mode="after")
    def require_contact(self):
        if not self.email and not self.phone:
            raise ValueError("Provide at least an email address or phone number")
        return self


class StudentUpdate(BaseModel):
    """All fields are optional so PATCH can change only selected fields."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    email: Optional[str] = Field(default=None, max_length=254)
    phone: Optional[str] = Field(default=None, max_length=30)
    course: Optional[str] = Field(default=None, max_length=100)
    address: Optional[str] = Field(default=None, max_length=250)
    enrollment_date: Optional[date] = None

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("Name cannot be blank")
        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: Optional[str]) -> Optional[str]:
        if value is None or value.strip() == "":
            return None
        value = value.strip().lower()
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
            raise ValueError("Enter a valid email address")
        return value

    @field_validator("phone")
    @classmethod
    def clean_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is None or value.strip() == "":
            return None
        return value.strip()


class StudentResponse(StudentBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
