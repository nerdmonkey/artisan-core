from datetime import datetime
from typing import List, Tuple
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session
from app.exceptions.user import InvalidSortFieldError, UserNotFoundError, DuplicateUserError
from app.models.user import User
from app.requests.user import UserCreateRequest, UserUpdateRequest
from app.responses.user import UserCreateResponse, UserResponse, UserUpdateResponse

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> User:
        user = self.db.query(User).filter(User.id == id).first()
        if not user:
            raise UserNotFoundError(f"User with ID {id} not found")
        return user

    def _user_to_response(self, user: User) -> UserResponse:
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            created_at=user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            updated_at=user.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        )

    def all(self, page=1, items_per_page=10, sort_type="asc", sort_by="id",
            email=None, username=None, start_date=None, end_date=None) -> Tuple[List[UserResponse], int, int, int, int]:

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
        query = query.order_by(asc(sort_column) if sort_type == "asc" else desc(sort_column))

        users = query.offset(offset).limit(items_per_page).all()
        total = query.count()

        users_response = [self._user_to_response(user) for user in users]

        return users_response, total, (total - 1) // items_per_page + 1, offset + 1, min(offset + items_per_page, total)


    def save(self, user_request: UserCreateRequest) -> UserCreateResponse:
        """Save a new user, checking for duplicates."""
        existing_user = self.db.query(User).filter(User.email == user_request.email).first()
        if existing_user:
            raise DuplicateUserError("User with this email already exists")

        user_data = user_request.model_dump(exclude_unset=True)
        user_data["password"] = "hashed_" + user_data["password"]
        new_user = User(**user_data)

        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return self._user_to_response(new_user)





    def update(self, id: int, user_request: UserUpdateRequest) -> UserUpdateResponse:
        """Update a user in the database."""
        user = self.get_by_id(id)
        update_data = user_request.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["password"] = "hashed_" + update_data["password"]

        for key, value in update_data.items():
            setattr(user, key, value)

        self.db.commit()
        self.db.refresh(user)
        return self._user_to_response(user)

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
