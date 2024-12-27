from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from app.helpers.database import db
from app.models.user import User


class UserFindRequest(BaseModel):
    id: int

    model_config = ConfigDict(from_attributes=True)

    @field_validator("id", mode="before")
    def check_id(cls, value):
        if value == 0:
            raise ValueError("Id must be greater than 0")

        existing_id = db().query(User).filter(User.id == value).first()

        if not existing_id:
            raise ValueError("User does not exist")


class UserCreateRequest(BaseModel):
    """
    Data model for creating a new user.

    Attributes:
        username (str): The username of the new user.
        email (EmailStr): The email address of the new user.
        password (str): The password for the new user.
    """

    username: str
    email: EmailStr
    password: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    model_config = ConfigDict(from_attributes=True)

    @field_validator("username", mode="before")
    def check_name(cls, value):
        existing_username = db().query(User).filter(User.username == value).first()

        if existing_username:
            raise ValueError("User with this username already exists")

        if not value.strip():
            raise ValueError("The name field is required")

        if len(value) < 3:
            raise ValueError("Name must be at least 3 characters long")

        if len(value) > 50:
            raise ValueError("Name must be at most 50 characters long")

        return value

    @field_validator("email", mode="before")
    def check_email(cls, value):
        if not value.strip():
            raise ValueError("The email field is required")

        existing_email = db().query(User).filter(User.email == value).first()

        if existing_email:
            raise ValueError("User with this email already exists")

        return value


class UserUpdateRequest(BaseModel):
    """
    Data model for updating an existing user.

    Attributes:
        username (Optional[str]): The new username of the user. Optional.
        email (Optional[EmailStr]): The new email address of the user. Optional.
        password (Optional[str]): The new password for the user. Optional.
    """

    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    model_config = ConfigDict(from_attributes=True)

    @field_validator("username", mode="before")
    def check_name(cls, value):
        if value is None:
            return value

        if not value.strip():
            raise ValueError("The name field is required")

        if len(value) < 3:
            raise ValueError("Name must be at least 3 characters long")

        if len(value) > 20:
            raise ValueError("Name must be at most 20 characters long")

        return value

    @field_validator("email", mode="before")
    def check_email(cls, value):
        if value is None:
            return value

        if not value.strip():
            raise ValueError("The email field is required")

        return value
