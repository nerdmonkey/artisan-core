from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class UserCreateRequest(BaseModel):
    """
    UserCreateRequest is a data model for creating a new user request.

    Attributes:
        username (str): The username of the user. Must be between 3 and 50 characters long.
        email (EmailStr): The email address of the user.
        password (str): The password for the user.
        created_at (datetime): The timestamp when the user was created. Defaults to the
                                current datetime.
        updated_at (datetime): The timestamp when the user was last updated. Defaults to
                                the current datetime.

    Methods:
        check_name(cls, value): Validates the username. Ensures it is not empty, and is
        between 3 and 50 characters long. check_email(cls, value): Validates the email.
        Ensures it is not empty.
    """

    username: str
    email: EmailStr
    password: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    model_config = ConfigDict(from_attributes=True)

    @field_validator("username", mode="before")
    def check_name(cls, value):
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

        return value


class UserUpdateRequest(BaseModel):
    """
    UserUpdateRequest is a Pydantic model for handling user update requests.

    Attributes:
        username (Optional[str]): The username of the user. Must be between 3 and 20 characters long if provided.
        email (Optional[EmailStr]): The email address of the user. Must be a valid email format if provided.
        password (Optional[str]): The password of the user.
        created_at (datetime): The timestamp when the user was created. Defaults to the current datetime.
        updated_at (datetime): The timestamp when the user was last updated. Defaults to the current datetime.

    Validators:
        check_name (str): Validates the username field. Ensures it is not empty, and is between 3
                            and 20 characters long if provided.
        check_email (str): Validates the email field. Ensures it is not empty if provided.
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
