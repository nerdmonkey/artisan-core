from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, field_serializer


class UserResponse(BaseModel):
    """
    UserResponse is a data model representing the response structure for user-related data.

    Attributes:
        id (int): The unique identifier for the user.
        username (str): The username of the user.
        email (str): The email address of the user.
        created_at (str): The timestamp when the user was created,
                            formatted as "YYYY-MM-DD HH:MM:SS".
        updated_at (str): The timestamp when the user was last updated,
                            formatted as "YYYY-MM-DD HH:MM:SS".

    Methods:
        created_at(cls, v: datetime) -> str:
            Serializes the created_at attribute to a string in the
            format "YYYY-MM-DD HH:MM:SS".

        updated_at(cls, v: datetime) -> str:
            Serializes the updated_at attribute to a string in the
            format "YYYY-MM-DD HH:MM:SS".
    """

    id: int
    username: str
    email: str
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("created_at")
    def created_at(cls, v: datetime) -> str:
        return v.strftime("%Y-%m-%d %H:%M:%S")

    @field_serializer("updated_at")
    def updated_at(cls, v: datetime) -> str:
        return v.strftime("%Y-%m-%d %H:%M:%S")


class SingleUserResponse(BaseModel):
    """
    SingleUserResponse is a response model for a single user.

    Attributes:
        data (UserResponse): The user data.
        status_code (int): The HTTP status code of the response.
    """

    data: UserResponse
    status_code: int


class Pagination(BaseModel):
    """
    A class to represent pagination details.

    Attributes:
    -----------
    current_page : int
        The current page number.
    last_page : int
        The last page number.
    first_item : int
        The index of the first item on the current page.
    last_item : int
        The index of the last item on the current page.
    items_per_page : int
        The number of items per page.
    total : int
        The total number of items.
    """

    current_page: int
    last_page: int
    first_item: int
    last_item: int
    items_per_page: int
    total: int


class PaginatedUserResponse(BaseModel):
    """
    PaginatedUserResponse is a model that represents a paginated response for user data.

    Attributes:
        data (List[UserResponse]): A list of user response objects.
        meta (Pagination): Pagination metadata for the response.
        status_code (int): The HTTP status code of the response.
    """

    data: List[UserResponse]
    meta: Pagination
    status_code: int


class UserCreateResponse(BaseModel):
    """
    UserCreateResponse is a Pydantic model representing the response data for user creation.

    Attributes:
        id (int): The unique identifier of the user.
        username (str): The username of the user.
        email (str): The email address of the user.
        created_at (str): The timestamp when the user was created.
        updated_at (str): The timestamp when the user was last updated.
    """

    id: int
    username: str
    email: str
    created_at: str
    updated_at: str


class UserUpdateResponse(BaseModel):
    """
    UserUpdateResponse is a Pydantic model that represents the response schema for updating a user.

    Attributes:
        id (int): The unique identifier of the user.
        username (str): The username of the user.
        email (str): The email address of the user.
        created_at (str): The timestamp when the user was created.
        updated_at (str): The timestamp when the user was last updated.
    """

    id: int
    username: str
    email: str
    created_at: str
    updated_at: str
