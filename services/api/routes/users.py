from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from models_auth import UserCreate, UserResponse, UserRole, UserUpdate
from security import get_current_user
from services import users as user_service

router = APIRouter(prefix="/users", tags=["Users"])


def _ensure_self_or_admin(target_user_id: int, current_user: dict[str, Any]) -> None:
    if current_user["id"] != target_user_id and current_user.get("role") != UserRole.admin.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado para acceder a este usuario")


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate):
    return user_service.create_user(user_data)


@router.get("", response_model=list[UserResponse])
def list_users(current_user: dict[str, Any] = Depends(get_current_user)):
    if current_user.get("role") != UserRole.admin.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo admin puede listar usuarios")
    return user_service.list_users()


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, current_user: dict[str, Any] = Depends(get_current_user)):
    _ensure_self_or_admin(user_id, current_user)
    user = user_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    updates: UserUpdate,
    current_user: dict[str, Any] = Depends(get_current_user),
):
    _ensure_self_or_admin(user_id, current_user)
    if current_user.get("role") != UserRole.admin.value and updates.role is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo admin puede cambiar roles")
    updated = user_service.update_user(user_id, updates)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return updated


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, current_user: dict[str, Any] = Depends(get_current_user)):
    _ensure_self_or_admin(user_id, current_user)
    target_user = user_service.get_user_by_id(user_id)
    if target_user is not None and target_user.get("role") == UserRole.admin.value and current_user.get("role") != UserRole.admin.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo admin puede eliminar una cuenta admin")
    if not user_service.delete_user(user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
