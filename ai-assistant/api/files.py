"""
File Operations API endpoints
"""
from fastapi import APIRouter, HTTPException
from ..schemas.file_ops import FileOperationRequest, FileOperationResponse
from ..services.file_operations import FileOperationsService
from typing import List

router = APIRouter(prefix="/files", tags=["files"])

file_service = FileOperationsService()


@router.post("/create")
async def create_file(request: FileOperationRequest):
    """Create a new file"""
    result = file_service.create_file(request.file_path, request.content or "")
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/read")
async def read_file(request: FileOperationRequest):
    """Read file contents"""
    result = file_service.read_file(request.file_path)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/edit")
async def edit_file(request: FileOperationRequest):
    """Edit file contents"""
    if not request.content:
        raise HTTPException(status_code=400, detail="Content is required for editing")

    result = file_service.edit_file(request.file_path, request.content)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/delete")
async def delete_file(request: FileOperationRequest):
    """Delete a file"""
    result = file_service.delete_file(request.file_path)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/move")
async def move_file(request: FileOperationRequest):
    """Move a file"""
    if not request.new_path:
        raise HTTPException(status_code=400, detail="new_path is required for moving")

    result = file_service.move_file(request.file_path, request.new_path)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/copy")
async def copy_file(request: FileOperationRequest):
    """Copy a file"""
    if not request.new_path:
        raise HTTPException(status_code=400, detail="new_path is required for copying")

    result = file_service.copy_file(request.file_path, request.new_path)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/list")
async def list_files(directory: str = "", pattern: str = "*"):
    """List files in a directory"""
    result = file_service.list_files(directory, pattern)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    return result
