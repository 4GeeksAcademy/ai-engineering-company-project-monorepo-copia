from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from models_auth import ProfileMeResponse, ProfileUpdate
from security import get_current_user
from services import profiles as profile_service

router = APIRouter(prefix="/profiles", tags=["Profiles"])


@router.get("/me", response_model=ProfileMeResponse)
def get_my_profile(current_user: dict[str, Any] = Depends(get_current_user)):
    profile = profile_service.get_profile_by_user_id(current_user["id"])
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil no encontrado")
    return profile


@router.put("/me", response_model=ProfileMeResponse)
def update_my_profile(
    updates: ProfileUpdate,
    current_user: dict[str, Any] = Depends(get_current_user),
):
    profile = profile_service.get_profile_by_user_id(current_user["id"])
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil no encontrado")
    updated = profile_service.update_profile(profile["id"], updates)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil no encontrado")
    return updated
