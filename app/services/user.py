from datetime import datetime
from typing import List, Tuple

from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from app.exceptions.user import (
    DuplicateUserError,
    InvalidSortFieldError,
    UserNotFoundError,
)
from app.models.user import User
from app.requests.user import UserCreateRequest, UserUpdateRequest
from app.responses.user import UserCreateResponse, UserResponse, UserUpdateResponse


class UserService:
    def __init__(self, db: Session):
        """
        Initializes the User service with a database session.

        Args:
            db (Session): The database session to be used by the service.
        """
        self.db = db

    def get_by_id(self, id: int) -> User:
        """
        Retrieve a user by their ID.

        Args:
            id (int): The ID of the user to retrieve.

        Returns:
            User: The user object corresponding to the given ID.

        Raises:
            UserNotFoundError: If no user with the given ID is found.
        """
        user = self.db.query(User).filter(User.id == id).first()
        if not user:
            raise UserNotFoundError(f"User with ID {id} not found")
        return user

    def _user_to_response(self, user: User) -> UserResponse:
        """
        Converts a User object to a UserResponse object.

        Args:
            user (User): The user object to convert.

        Returns:
            UserResponse: The converted user response object containing the user's id, username, email,
                          created_at, and updated_at fields formatted as strings.
        """
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            created_at=user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            updated_at=user.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        )

    def all(
        self,
        page=1,
        items_per_page=10,
        sort_type="asc",
        sort_by="id",
        email=None,
        username=None,
        start_date=None,
        end_date=None,
    ) -> Tuple[List[UserResponse], int, int, int, int]:
        """
        Retrieve a paginated list of users with optional filtering and sorting.

        Args:
            page (int, optional): The page number to retrieve. Defaults to 1.
            items_per_page (int, optional): The number of items per page. Defaults to 10.
            sort_type (str, optional): The sort order, either 'asc' or 'desc'. Defaults to "asc".
            sort_by (str, optional): The field to sort by. Defaults to "id".
            email (str, optional): Filter by email. Defaults to None.
            username (str, optional): Filter by username. Defaults to None.
            start_date (datetime, optional): Filter by start date (inclusive). Defaults to None.
            end_date (datetime, optional): Filter by end date (inclusive). Defaults to None.

        Returns:
            Tuple[List[UserResponse], int, int, int, int]: A tuple containing:
                - A list of UserResponse objects for the current page.
                - The total number of users.
                - The total number of pages.
                - The starting index of the current page.
                - The ending index of the current page.

        Raises:
            ValueError: If the sort_type is not 'asc' or 'desc'.
            InvalidSortFieldError: If the sort_by field is not a valid attribute of the User model.
        """
        if sort_type not in ["asc", "desc"]:
            raise ValueError("Invalid sort type; must be 'asc' or 'desc'")

        offset = (page - 1) * items_per_page
        query = self.db.query(User)

        if username:
            query = query.filter(User.username == username)
        if start_date:
            query = query.filter(User.created_at >= start_date)
        if end_date:
            query = query.filter(User.created_at <= end_date)

        if not hasattr(User, sort_by):
            raise InvalidSortFieldError("Invalid sort field")

        sort_column = getattr(User, sort_by)
        query = query.order_by(
            asc(sort_column) if sort_type == "asc" else desc(sort_column)
        )

        users = query.offset(offset).limit(items_per_page).all()
        total = query.count()

        users_response = [self._user_to_response(user) for user in users]

        return (
            users_response,
            total,
            (total - 1) // items_per_page + 1,
            offset + 1,
            min(offset + items_per_page, total),
        )

    def save(self, user_request: UserCreateRequest) -> UserCreateResponse:
        """
        Saves a new user to the database.

        Args:
            user_request (UserCreateRequest): The request object containing user details.

        Returns:
            UserCreateResponse: The response object containing the created user's details.

        Raises:
            DuplicateUserError: If a user with the given email already exists.
        """

        existing_user = (
            self.db.query(User).filter(User.email == user_request.email).first()
        )
        if existing_user:
            raise DuplicateUserError("User with this email already exists")

        user_data = user_request.model_dump(exclude_unset=True)
        user_data["password"] = "hashed_" + user_data["password"]

        new_user = User(**user_data)

        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)

        return UserCreateResponse(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            created_at=new_user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            updated_at=new_user.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        )

    def update(self, id: int, user_request: UserUpdateRequest) -> UserUpdateResponse:
        """
        Updates an existing user with the provided data.
        Args:
            id (int): The ID of the user to update.
            user_request (UserUpdateRequest): The request object containing the updated user data.
        Returns:
            UserUpdateResponse: The response object containing the updated user data.
        Raises:
            UserNotFoundException: If no user with the given ID is found.
        """

        user = self.get_by_id(id)
        update_data = user_request.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["password"] = "hashed_" + update_data["password"]

        for key, value in update_data.items():
            setattr(user, key, value)

        self.db.commit()
        self.db.refresh(user)

        return UserUpdateResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            created_at=user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            updated_at=user.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        )

    def delete(self, id: int) -> UserResponse:
        """
        Delete a user by ID.

        Args:
            id (int): The ID of the user to delete.

        Returns:
            UserResponse: The deleted user information.

        Raises:
            UserNotFoundError: If the user is not found.
        """

        user = self.get_by_id(id)
        response = self._user_to_response(user)
        try:
            self.db.delete(user)
            self.db.commit()
            return response
        except Exception as e:
            self.db.rollback()
            raise e

    def bulk_delete(self, user_ids: List[int]) -> List[int]:
        """
        Delete multiple users by their IDs.

        Args:
            user_ids (List[int]): A list of user IDs to delete.

        Returns:
            List[int]: A list of IDs of deleted users.

        Raises:
            UserNotFoundError: If no users are found for the given IDs.
        """

        try:
            users_to_delete = self.db.query(User).filter(User.id.in_(user_ids)).all()
            if not users_to_delete:
                raise UserNotFoundError("No users found for the given IDs")

            deleted_user_ids = [user.id for user in users_to_delete]
            for user in users_to_delete:
                self.db.delete(user)

            self.db.commit()
            return deleted_user_ids
        except Exception as e:
            self.db.rollback()
            raise e

    def find(self, id: int) -> UserResponse:
        """
        Find a user by their ID and return the user response.

        Args:
            id (int): The ID of the user.

        Returns:
            UserResponse: The user response.

        Raises:
            UserNotFoundError: If the user is not found.
        """
        user = self.get_by_id(id)
        return self._user_to_response(user)

    def total(self) -> int:
        """Get the total number of users."""
        return self.db.query(User).count()
