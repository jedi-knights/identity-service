"""User management routes."""
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from identity_service.api.dependencies.database import get_db_session
from identity_service.application.dto.schemas import UserCreate, UserResponse
from identity_service.application.use_cases.user_service import UserService
from identity_service.infrastructure.container import Container

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@inject
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db_session),
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> UserResponse:
    """Create a new user."""
    # Pass the session to repository
    user_service.user_repository.session = db

    try:
        user = await user_service.create_user(
            username=user_data.username, email=user_data.email, password=user_data.password
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.get("/{user_id}", response_model=UserResponse)
@inject
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> UserResponse:
    """Get a user by ID."""
    # Pass the session to repository
    user_service.user_repository.session = db

    user = await user_service.get_user_by_id(user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.post("/{user_id}/deactivate", response_model=UserResponse)
@inject
async def deactivate_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> UserResponse:
    """Deactivate a user."""
    # Pass the session to repository
    user_service.user_repository.session = db

    try:
        user = await user_service.deactivate_user(user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )
