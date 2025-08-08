# Copyright 2024 Google LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Request
from typing import List, Optional
from service.firestore import get_user_settings, set_user_settings, get_saved_settings, save_setting, delete_saved_setting, get_saved_setting_by_id
from service.storage import upload_gcs_file
from google.cloud import storage
import uuid

router = APIRouter()

# Dependency to extract userId from token (stub, replace with real auth)
def get_user_id(request: Request):
    # TODO: Implement real token-based authentication
    user_id = request.headers.get("X-User-Id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user_id

@router.get("/settings/{userId}")
def get_settings(userId: str, user_id: str = Depends(get_user_id)):
    if userId != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    settings = get_user_settings(user_id)
    if not settings:
        # Return default settings and save to DB if not found
        settings = {
            "brandName": "",
            "logoUrl": "",
            "primaryColor": "#1976d2"
        }
        set_user_settings(user_id, settings)
    return settings

@router.post("/settings/{userId}")
def post_settings(userId: str, payload: dict, user_id: str = Depends(get_user_id)):
    if userId != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    set_user_settings(user_id, payload)
    return {"success": True}

@router.get("/saved-settings/{userId}")
def get_saved_settings_api(userId: str, user_id: str = Depends(get_user_id)):
    if userId != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return get_saved_settings(user_id)

@router.post("/saved-settings/{userId}")
def post_saved_settings(userId: str, payload: dict, user_id: str = Depends(get_user_id)):
    if userId != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    setting_id = save_setting(user_id, payload)
    return {"settingId": setting_id}

@router.delete("/saved-settings/{userId}/{settingId}")
def delete_saved_setting_api(userId: str, settingId: str, user_id: str = Depends(get_user_id)):
    if userId != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    delete_saved_setting(user_id, settingId)
    return {"success": True}

@router.post("/upload-logo/{userId}")
def upload_logo(userId: str, file: UploadFile = File(...), user_id: str = Depends(get_user_id)):
    if userId != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    filename = f"logos/{user_id}/{uuid.uuid4()}_{file.filename}"
    url = upload_gcs_file(file.file, filename)
    return {"logoUrl": url}

@router.get("/saved-settings/{userId}/{settingId}")
def get_saved_setting_api(userId: str, settingId: str, user_id: str = Depends(get_user_id)):
    if userId != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    setting = get_saved_setting_by_id(user_id, settingId)
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting
