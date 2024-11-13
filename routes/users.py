from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.exceptions.user import (
    DuplicateUserError,
    InvalidSortFieldError,
    UserNotFoundError,
)
from app.requests.user import UserCreateRequest, UserUpdateRequest
from app.responses.user import (
    PaginatedUserResponse,
    SingleUserResponse,
    UserCreateResponse,
)
from app.services.user import UserService
from config.database import db


def get_user_service(db: Session = Depends(db)) -> UserService:
    """
    Provides an instance of UserService with a database session.

    Args:
        db (Session, optional): The database session dependency. Defaults to Depends(db).

    Returns:
        UserService: An instance of UserService initialized with the provided database session.
    """
    return UserService(db=db)


route = APIRouter(
    prefix="/api", tags=["Users"], responses={404: {"description": "Not found"}}
)


@route.get("/users", status_code=200, response_model=PaginatedUserResponse)
async def get_users(
    page: Optional[int] = Query(1, description="page number", gt=0),
    items_per_page: Optional[int] = Query(10, description="items per page", gt=0),
    sort_type: Optional[str] = Query("asc", description="sort type (asc or desc)"),
    sort_by: Optional[str] = Query("id", description="sort by field"),
    username: Optional[str] = Query(None, description="username filter"),
    email: Optional[str] = Query(None, description="email filter"),
    start_date: Optional[date] = Query(None, description="start date filter"),
    end_date: Optional[date] = Query(None, description="end date filter"),
    user_service: UserService = Depends(get_user_service),
):
    """
    Args:
        page (Optional[int]): Page number for pagination (default is 1).
        items_per_page (Optional[int]): Number of items per page (default is 10).
        sort_type (Optional[str]): Sort type, either 'asc' or 'desc' (default is 'asc').
        sort_by (Optional[str]): Field to sort by (default is 'id').
        username (Optional[str]): Filter by username.
        email (Optional[str]): Filter by email.
        start_date (Optional[date]): Filter by start date.
        end_date (Optional[date]): Filter by end date.
        user_service (UserService): Dependency injection for user service.

    Returns:
        dict: A dictionary containing the list of users, pagination metadata, and status code.

    Raises:
        HTTPException: If an invalid sort field is provided (status code 400).
        HTTPException: If an unexpected error occurs (status code 500).
    """
    try:
        items, total, last_page, first_item, last_item = user_service.all(
            page=page,
            items_per_page=items_per_page,
            sort_type=sort_type,
            sort_by=sort_by,
            start_date=start_date,
            end_date=end_date,
            username=username,
            email=email,
        )

        if not items:
            return {
                "data": [],
                "meta": {
                    "current_page": 0,
                    "last_page": 0,
                    "first_item": 0,
                    "last_item": 0,
                    "items_per_page": 0,
                    "total": 0,
                },
                "status_code": 404,
            }

        return {
            "data": items,
            "meta": {
                "current_page": page,
                "last_page": last_page,
                "first_item": first_item,
                "last_item": last_item,
                "items_per_page": items_per_page,
                "total": total,
            },
            "status_code": 200,
        }
    except InvalidSortFieldError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")


@route.get("/users/{id}", status_code=200, response_model=SingleUserResponse)
async def get_user(
    id: int = Path(..., title="The ID of the user to get", gt=0),
    user_service: UserService = Depends(get_user_service),
):
    """
    Retrieve a user by ID.

    Args:
        id (int): The ID of the user to get. Must be greater than 0.
        user_service (UserService): Dependency injection for the user service.

    Returns:
        dict: A dictionary containing the user data and status code.

    Raises:
        HTTPException: If the user is not found (404), validation fails (422), or an unexpected error occurs (500).
    """
    try:
        user = user_service.find(id)
        return {"data": user, "status_code": 200}
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")


@route.post("/users/{id}", status_code=201, response_model=UserCreateResponse)
async def create_user(
    user_request: UserCreateRequest,
    user_service: UserService = Depends(get_user_service),
):
    """
    Create a new user.

    Args:
        user_request (UserCreateRequest): The request body containing user creation details.
        user_service (UserService): The UserService dependency for handling user operations.

    Returns:
        UserCreateResponse: The response data of the created user.

    Raises:
        HTTPException: If a user with the same email already exists.
    """
    try:
        created_user = user_service.save(user_request)
        return created_user
    except DuplicateUserError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the user: {str(e)}",
        )


@route.put("/users/{id}", status_code=200, response_model=SingleUserResponse)
async def update_user(
    user_request: UserUpdateRequest,
    id: int = Path(..., title="The ID of the user to update", gt=0),
    user_service: UserService = Depends(get_user_service),
):
    """
    Update an existing user.

    Args:
        user_request (UserUpdateRequest): The request object containing user update information.
        id (int): The ID of the user to update. Must be greater than 0.
        user_service (UserService): The user service dependency.

    Returns:
        dict: A dictionary containing the updated user data and status code.

    Raises:
        HTTPException: If the user is not found (404) or any other exception occurs (500).
    """
    try:
        updated_user = user_service.update(id, user_request)
        return {"data": updated_user, "status_code": 200}
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@route.delete("/users/{id}", status_code=200, response_model=SingleUserResponse)
async def delete_user(
    id: int = Path(..., title="The ID of the user to delete", gt=0),
    user_service: UserService = Depends(get_user_service),
):
    """
    Delete a user by ID.

    Args:
        id (int): The ID of the user to delete. Must be greater than 0.
        user_service (UserService): The user service dependency.

    Returns:
        dict: A dictionary containing the deleted user data and status code 200.

    Raises:
        HTTPException: If the user is not found (status code 404).
        HTTPException: If an unexpected error occurs (status code 500).
    """
    try:
        user = user_service.delete(id)
        return {"data": user, "status_code": 200}
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")


@route.delete("/users/{ids}/bulk", status_code=status.HTTP_200_OK)
async def batch_delete_users(
    ids: str = Path(..., description="Comma-separated list of user IDs to delete"),
    user_service: UserService = Depends(get_user_service),
):
    """
    Batch delete multiple users by their IDs from the URL path.

    Args:
        user_ids (str): Comma-separated list of user IDs.
        user_service (UserService): UserService instance for handling user operations.

    Returns:
        dict: A dictionary with a message indicating the deletion status.

    Raises:
        HTTPException: If no users are found with the given IDs.
    """
    try:
        user_id_list = [int(user_id.strip()) for user_id in ids.split(",")]

        deleted_user_ids = user_service.bulk_delete(user_id_list)
        return {"message": f"Deleted users with IDs: {deleted_user_ids}"}
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No users found for the given IDs",
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid format for user IDs. Please provide a comma-separated list of integers.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting users: {str(e)}",
        )
