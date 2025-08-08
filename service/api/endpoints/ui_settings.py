# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""FastAPI endpoint for UI settings management."""

import os
import logging
import json
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from pydantic import BaseModel
from google.cloud import firestore
import google.auth
import google.auth.transport.requests

# Assuming these are correctly set up and available in your environment
from services.storage_service import storage_service
import utils

logger = logging.getLogger(__name__)

# Application ID, typically from environment variables
APP_ID = os.environ.get('__app_id', 'dreamboard-default-app-id')
# Firestore Database ID, ensure this matches your project's configuration
FIRESTORE_DATABASE_ID = "dreamboard-db"

def get_firestore_client():
    """Initializes and returns a Firestore client."""
    try:
        project_id = os.getenv("PROJECT_ID")
        logger.info(f"Initializing Firestore client for project: {project_id}, database: {FIRESTORE_DATABASE_ID}")
        client = firestore.Client(project=project_id, database=FIRESTORE_DATABASE_ID)
        logger.info(f"Firestore client initialized successfully for project: {client.project}")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Firestore client in ui_settings_routes: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to connect to Firestore: {e}")

class UpdateSettingsResponse(BaseModel):
    """Pydantic model for the response of the update_app_settings endpoint."""
    message: str
    logo_url: Optional[str] = None
    brand_name: str
    color: str
    user_id: str

ui_settings_router = APIRouter(prefix="/ui_settings")

@ui_settings_router.post("/update_settings", response_model=UpdateSettingsResponse)
async def update_app_settings(
    brand_name: str = Form(...),
    color: str = Form(...),
    user_id: str = Form(...), # User ID now comes from the request body as a Form parameter
    logo_file: Optional[UploadFile] = File(None),
    db_client: firestore.Client = Depends(get_firestore_client)
):
    """
    Handles the update of application settings, including logo upload to GCS
    and data storage in Firestore.
    """
    # Define a static document ID for client-specific branding settings within Firestore.
    # This acts as the 'clientid' document as requested.
    CLIENT_BRANDING_DOC_ID = "branding_profile" 

    logo_url = "" # Initialize logo_url

    # Debugging: Log Google Cloud credentials and project information
    logger.info(f"DEBUG: GOOGLE_APPLICATION_CREDENTIALS env var: {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')}")
    try:
        credentials, project = google.auth.default()
        logger.info(f"DEBUG: Type of credentials from google.auth.default(): {type(credentials)}")
        logger.info(f"DEBUG: Project from google.auth.default(): {project}")
    except Exception as e:
        logger.error(f"DEBUG: Error getting default credentials: {e}")

    if logo_file:
        try:
            # Extract file extension from the uploaded logo's filename
            file_extension = os.path.splitext(logo_file.filename)[1]
            # Construct a unique filename for the logo within the GCS bucket.
            # The path includes the user_id for better organization within GCS.
            unique_filename_in_folder = f"user_logos/{user_id}/logo_{os.urandom(8).hex()}{file_extension}"

            # Upload the logo file to Google Cloud Storage using the storage_service
            uploaded_blob = storage_service.upload_authenticated_logo(
                blob_name=unique_filename_in_folder,
                file_data=logo_file.file,
                mime_type=logo_file.content_type
            )
            
            # Generate a signed URL for the uploaded logo, allowing temporary public access
            # The full blob name for signing includes the storage service's root folder name
            full_blob_name_for_signing = f"{storage_service.storage_folder_name}/{unique_filename_in_folder}"
            logo_url = utils.get_signed_uri_from_gcs_uri(full_blob_name_for_signing)

            logger.info(f"Authenticated logo uploaded and signed URL generated: {logo_url}")

        except Exception as e:
            logger.error(f"Failed to upload logo or generate signed URL: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to process logo: {e}")

    try:
        # Construct the Firestore document reference based on the requested path:
        # `users/{userId}/appSettings/{clientid_document_name}`
        # Where `clientid_document_name` is `CLIENT_BRANDING_DOC_ID` ("branding_profile").
        settings_doc_ref = db_client.collection(f"users/{user_id}/appSettings").document(CLIENT_BRANDING_DOC_ID)
        
        # Prepare the data to be stored in Firestore
        settings_data = {
            "brand_name": brand_name,
            "logo_url": logo_url,
            "color": color,
            "last_updated": firestore.SERVER_TIMESTAMP # Automatically set the last update timestamp
        }

        # Use set() to create the document if it doesn't exist, or overwrite it if it does.
        settings_doc_ref.set(settings_data)
        logger.info(f"Settings saved to Firestore for user {user_id} under document {CLIENT_BRANDING_DOC_ID}: {settings_data}")

    except Exception as e:
        logger.error(f"Failed to save settings to Firestore for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save settings to database: {e}")

    # Return a success response with the updated settings information
    return UpdateSettingsResponse(
        message="Settings updated successfully",
        logo_url=logo_url,
        brand_name=brand_name,
        color=color,
        user_id=user_id
    )
