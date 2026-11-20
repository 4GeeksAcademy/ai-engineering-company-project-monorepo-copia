from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import HTTPException, status
from tinydb import Query

from database import profiles_table, users_table
from models_auth import UserCreate, UserRole, UserUpdate
from security import hash_password

UserQuery = Query()


def create_user(user_data: UserCreate) -> dict[str, Any]:
    email = str(user_data.email).strip().lower()
    if get_user_by_email(email) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El email ya está registrado")

    profile_data = {
        "name": user_data.name or user_data.full_name,
        "phone": user_data.phone,
        "address": user_data.address,
    }
    data = user_data.model_dump(exclude={"password", "name", "phone", "address"})
    data["email"] = email
    data["role"] = UserRole.user.value
    data["hashed_password"] = hash_password(user_data.password)
    data["created_at"] = datetime.now(timezone.utc).isoformat()
    user_id = users_table.insert(data)
    data["id"] = user_id
    try:
        from services.profiles import create_profile
        from models_auth import ProfileCreate

        create_profile_data = ProfileCreate(user_id=user_id, **profile_data)
        create_profile(create_profile_data)
    except Exception:
        users_table.remove(doc_ids=[user_id])
        raise
    return data


def get_user_by_id(user_id: int) -> Optional[dict[str, Any]]:
    user = users_table.get(doc_id=user_id)
    if user is None:
        return None
    result = dict(user)
    result["id"] = user_id
    return result


def list_users() -> list[dict[str, Any]]:
    users: list[dict[str, Any]] = []
    for user in users_table:
        result = dict(user)
        result["id"] = user.doc_id
        users.append(result)
    return users


def get_user_by_email(email: str) -> Optional[dict[str, Any]]:
    normalized_email = email.strip().lower()
    user = users_table.get(UserQuery.email == normalized_email)
    if user is None:
        # Legacy/case-variant records are checked without assuming normalized input.
        user = next(
            (item for item in users_table if str(item.get("email", "")).lower() == normalized_email),
            None,
        )
    if user is None:
        return None
    result = dict(user)
    result["id"] = user.doc_id
    return result


def update_user(user_id: int, updates: UserUpdate) -> Optional[dict[str, Any]]:
    user = get_user_by_id(user_id)
    if user is None:
        return None

    update_data = updates.model_dump(exclude_unset=True, exclude_none=True)
    if "email" in update_data:
        normalized_email = str(update_data["email"]).strip().lower()
        existing = get_user_by_email(normalized_email)
        if existing is not None and existing["id"] != user_id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El email ya está registrado")
        update_data["email"] = normalized_email
    if "role" in update_data:
        update_data["role"] = UserRole(update_data["role"]).value
    if "password" in update_data:
        update_data["hashed_password"] = hash_password(update_data.pop("password"))

    if update_data:
        users_table.update(update_data, doc_ids=[user_id])
    return get_user_by_id(user_id)


def delete_user(user_id: int) -> bool:
    if not users_table.contains(doc_id=user_id):
        return False
    profiles_table.remove(UserQuery.user_id == user_id)
    users_table.remove(doc_ids=[user_id])
    return True
