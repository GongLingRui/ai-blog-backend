"""
File Upload API endpoints
"""
import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.middlewares.auth import get_current_user
from app.models.user import User
from app.config import settings

router = APIRouter()

# Allowed file extensions
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}
ALLOWED_FILE_EXTENSIONS = {".pdf", ".doc", ".docx", ".txt", ".md"}

# Max file sizes (in bytes)
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB


class UploadResponse(BaseModel):
    """Upload response schema"""

    filename: str
    file_path: str
    file_url: str
    file_size: int
    content_type: str


class BatchUploadResponse(BaseModel):
    """Batch upload response schema"""

    successful: List[UploadResponse]
    failed: List[dict]


def validate_file_type(filename: str, allowed_extensions: set) -> bool:
    """Validate file type"""
    return os.path.splitext(filename)[1].lower() in allowed_extensions


def generate_unique_filename(original_filename: str) -> str:
    """Generate unique filename"""
    ext = os.path.splitext(original_filename)[1].lower()
    unique_id = str(uuid.uuid4())
    return f"{unique_id}{ext}"


async def save_upload_file(
    upload_file: UploadFile,
    upload_dir: str,
    max_size: int,
    allowed_extensions: set,
) -> UploadResponse:
    """Save uploaded file to disk"""

    # Validate file type
    if not validate_file_type(upload_file.filename, allowed_extensions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}",
        )

    # Generate unique filename
    unique_filename = generate_unique_filename(upload_file.filename)
    file_path = os.path.join(upload_dir, unique_filename)

    # Ensure upload directory exists
    os.makedirs(upload_dir, exist_ok=True)

    # Save file
    try:
        file_size = 0
        with open(file_path, "wb") as buffer:
            while chunk := await upload_file.read(8192):  # 8KB chunks
                file_size += len(chunk)
                if file_size > max_size:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"File too large. Maximum size: {max_size / (1024 * 1024)}MB",
                    )
                buffer.write(chunk)

        # Generate file URL
        file_url = f"{settings.API_V1_STR}/uploads/{unique_filename}"

        return UploadResponse(
            filename=upload_file.filename,
            file_path=file_path,
            file_url=file_url,
            file_size=file_size,
            content_type=upload_file.content_type or "application/octet-stream",
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Clean up file if save failed
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}",
        )


@router.post("/image", response_model=UploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a single image file
    Max size: 10MB
    Allowed formats: jpg, jpeg, png, gif, webp, svg
    """
    upload_dir = os.path.join(settings.BASE_DIR, "uploads", "images")

    result = await save_upload_file(
        file,
        upload_dir,
        MAX_IMAGE_SIZE,
        ALLOWED_IMAGE_EXTENSIONS,
    )

    return {
        "success": True,
        "data": result,
    }


@router.post("/images", response_model=BatchUploadResponse)
async def upload_images(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
):
    """
    Upload multiple image files
    Max size per file: 10MB
    Allowed formats: jpg, jpeg, png, gif, webp, svg
    """
    upload_dir = os.path.join(settings.BASE_DIR, "uploads", "images")

    successful = []
    failed = []

    for file in files:
        try:
            result = await save_upload_file(
                file,
                upload_dir,
                MAX_IMAGE_SIZE,
                ALLOWED_IMAGE_EXTENSIONS,
            )
            successful.append(result)
        except HTTPException as e:
            failed.append({"filename": file.filename, "error": e.detail})
        except Exception as e:
            failed.append({"filename": file.filename, "error": str(e)})

    return {
        "success": True,
        "data": {
            "successful": successful,
            "failed": failed,
            "total_requested": len(files),
            "total_successful": len(successful),
        },
    }


@router.post("/file", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a single file
    Max size: 20MB
    Allowed formats: pdf, doc, docx, txt, md
    """
    upload_dir = os.path.join(settings.BASE_DIR, "uploads", "files")

    result = await save_upload_file(
        file,
        upload_dir,
        MAX_FILE_SIZE,
        ALLOWED_FILE_EXTENSIONS,
    )

    return {
        "success": True,
        "data": result,
    }


@router.delete("/{filename}")
async def delete_uploaded_file(
    filename: str,
    file_type: str = Query(..., regex="^(image|file)$"),
    current_user: User = Depends(get_current_user),
):
    """
    Delete an uploaded file
    """
    # Determine upload directory based on file type
    if file_type == "image":
        upload_dir = os.path.join(settings.BASE_DIR, "uploads", "images")
    else:
        upload_dir = os.path.join(settings.BASE_DIR, "uploads", "files")

    file_path = os.path.join(upload_dir, filename)

    # Check if file exists
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )

    # Delete file
    try:
        os.remove(file_path)
        return {"success": True, "message": "File deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}",
        )


@router.get("/stats")
async def get_upload_stats(
    current_user: User = Depends(get_current_user),
):
    """
    Get upload statistics
    """
    upload_dirs = {
        "images": os.path.join(settings.BASE_DIR, "uploads", "images"),
        "files": os.path.join(settings.BASE_DIR, "uploads", "files"),
    }

    stats = {}

    for file_type, upload_dir in upload_dirs.items():
        if os.path.exists(upload_dir):
            files = [
                f
                for f in os.listdir(upload_dir)
                if os.path.isfile(os.path.join(upload_dir, f))
            ]
            total_size = sum(
                os.path.getsize(os.path.join(upload_dir, f)) for f in files
            )
            stats[file_type] = {
                "file_count": len(files),
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
            }
        else:
            stats[file_type] = {
                "file_count": 0,
                "total_size_bytes": 0,
                "total_size_mb": 0,
            }

    return {
        "success": True,
        "data": stats,
    }
