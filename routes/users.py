from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.exceptions.user import (
    DuplicateUserError,
    InvalidSortFieldError,
    UserNotFoundError,
)
from app.requests.user import UserCreateRequest, UserUpdateRequest
from app.responses.user import PaginatedUserResponse, SingleUserResponse
from app.services.user import UserService
from config.database import db


# Dependency to create a new UserService with each request
def get_user_service(db: Session = Depends(db)) -> UserService:
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
    Get a list of users with pagination and optional filters.
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
    Get a user by their unique identifier.
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


@route.put("/users/{id}", status_code=200, response_model=SingleUserResponse)
async def update_user(
    user_request: UserUpdateRequest,
    id: int = Path(..., title="The ID of the user to update", gt=0),
    user_service: UserService = Depends(get_user_service),
):
    """
    Update an existing user's information.
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
    Delete a user by their unique identifier.
    """
    try:
        user = user_service.delete(id)
        return {"data": user, "status_code": 200}
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
