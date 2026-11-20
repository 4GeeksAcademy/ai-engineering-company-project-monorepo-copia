from datetime import datetime, timezone
from typing import Any, Optional

from tinydb import Query

from database import profiles_table
from models_auth import ProfileCreate, ProfileUpdate

ProfileQuery = Query()


def create_profile(profile_data: ProfileCreate) -> dict[str, Any]:
    data = profile_data.model_dump()
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    profile_id = profiles_table.insert(data)
    data["id"] = profile_id
    return data


def get_profile_by_id(profile_id: int) -> Optional[dict[str, Any]]:
    profile = profiles_table.get(doc_id=profile_id)
    if profile is None:
        return None
    result = dict(profile)
    result["id"] = profile_id
    return result


def get_profile_by_user_id(user_id: int) -> Optional[dict[str, Any]]:
    profile = profiles_table.get(ProfileQuery.user_id == user_id)
    if profile is None:
        return None
    result = dict(profile)
    result["id"] = profile.doc_id
    return result


def get_profile_by_email(email: str) -> Optional[dict[str, Any]]:
    from services.users import get_user_by_email

    user = get_user_by_email(email)
    if user is None:
        return None
    return get_profile_by_user_id(user["id"])


def update_profile(profile_id: int, updates: ProfileUpdate) -> Optional[dict[str, Any]]:
    profile = get_profile_by_id(profile_id)
    if profile is None:
        return None
    update_data = updates.model_dump(exclude_unset=True, exclude_none=True)
    if update_data:
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        profiles_table.update(update_data, doc_ids=[profile_id])
    return get_profile_by_id(profile_id)


def delete_profile(profile_id: int) -> bool:
    if not profiles_table.contains(doc_id=profile_id):
        return False
    profiles_table.remove(doc_ids=[profile_id])
    return True
