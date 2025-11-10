"""
File Operations Service
Handles file operations with safety checks
"""
import os
import shutil
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path
from ..core.config import settings


class FileOperationsService:
    """Service for safe file operations"""

    def __init__(self):
        self.workspace_dir = settings.WORKSPACE_DIR
        self.max_file_size = settings.MAX_FILE_SIZE
        self.allowed_extensions = settings.ALLOWED_FILE_EXTENSIONS

    def _validate_path(self, file_path: str) -> tuple[bool, str]:
        """Validate file path for safety"""
        # Convert to absolute path
        abs_path = os.path.abspath(file_path)

        # Check if path is within workspace
        if not abs_path.startswith(self.workspace_dir):
            return False, "File path must be within workspace directory"

        # Check for path traversal attempts
        if ".." in file_path:
            return False, "Path traversal not allowed"

        return True, ""

    def _validate_extension(self, file_path: str) -> bool:
        """Check if file extension is allowed"""
        extension = os.path.splitext(file_path)[1].lower()
        return extension in self.allowed_extensions or extension == ""

    def create_file(self, file_path: str, content: str = "") -> Dict[str, Any]:
        """Create a new file"""
        # Make path relative to workspace
        full_path = os.path.join(self.workspace_dir, file_path)

        # Validate
        is_valid, error_msg = self._validate_path(full_path)
        if not is_valid:
            return {"success": False, "error": error_msg}

        if not self._validate_extension(full_path):
            return {"success": False, "error": "File extension not allowed"}

        # Check if file already exists
        if os.path.exists(full_path):
            return {"success": False, "error": "File already exists"}

        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            # Write file
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return {
                "success": True,
                "file_path": full_path,
                "file_name": os.path.basename(full_path),
                "file_size": len(content.encode('utf-8'))
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def read_file(self, file_path: str) -> Dict[str, Any]:
        """Read file contents"""
        full_path = os.path.join(self.workspace_dir, file_path)

        # Validate
        is_valid, error_msg = self._validate_path(full_path)
        if not is_valid:
            return {"success": False, "error": error_msg}

        if not os.path.exists(full_path):
            return {"success": False, "error": "File not found"}

        if not os.path.isfile(full_path):
            return {"success": False, "error": "Path is not a file"}

        try:
            # Check file size
            file_size = os.path.getsize(full_path)
            if file_size > self.max_file_size:
                return {"success": False, "error": f"File too large (max {self.max_file_size} bytes)"}

            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return {
                "success": True,
                "file_path": full_path,
                "file_name": os.path.basename(full_path),
                "file_size": file_size,
                "content": content
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def edit_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Edit existing file"""
        full_path = os.path.join(self.workspace_dir, file_path)

        # Validate
        is_valid, error_msg = self._validate_path(full_path)
        if not is_valid:
            return {"success": False, "error": error_msg}

        if not os.path.exists(full_path):
            return {"success": False, "error": "File not found"}

        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return {
                "success": True,
                "file_path": full_path,
                "file_name": os.path.basename(full_path),
                "file_size": len(content.encode('utf-8'))
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_file(self, file_path: str) -> Dict[str, Any]:
        """Delete a file"""
        full_path = os.path.join(self.workspace_dir, file_path)

        # Validate
        is_valid, error_msg = self._validate_path(full_path)
        if not is_valid:
            return {"success": False, "error": error_msg}

        if not os.path.exists(full_path):
            return {"success": False, "error": "File not found"}

        try:
            os.remove(full_path)
            return {
                "success": True,
                "file_path": full_path,
                "file_name": os.path.basename(full_path)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def move_file(self, source_path: str, dest_path: str) -> Dict[str, Any]:
        """Move a file"""
        full_source = os.path.join(self.workspace_dir, source_path)
        full_dest = os.path.join(self.workspace_dir, dest_path)

        # Validate both paths
        is_valid, error_msg = self._validate_path(full_source)
        if not is_valid:
            return {"success": False, "error": f"Source: {error_msg}"}

        is_valid, error_msg = self._validate_path(full_dest)
        if not is_valid:
            return {"success": False, "error": f"Destination: {error_msg}"}

        if not os.path.exists(full_source):
            return {"success": False, "error": "Source file not found"}

        try:
            # Create destination directory if needed
            os.makedirs(os.path.dirname(full_dest), exist_ok=True)
            shutil.move(full_source, full_dest)

            return {
                "success": True,
                "source_path": full_source,
                "dest_path": full_dest,
                "file_name": os.path.basename(full_dest)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def copy_file(self, source_path: str, dest_path: str) -> Dict[str, Any]:
        """Copy a file"""
        full_source = os.path.join(self.workspace_dir, source_path)
        full_dest = os.path.join(self.workspace_dir, dest_path)

        # Validate both paths
        is_valid, error_msg = self._validate_path(full_source)
        if not is_valid:
            return {"success": False, "error": f"Source: {error_msg}"}

        is_valid, error_msg = self._validate_path(full_dest)
        if not is_valid:
            return {"success": False, "error": f"Destination: {error_msg}"}

        if not os.path.exists(full_source):
            return {"success": False, "error": "Source file not found"}

        try:
            # Create destination directory if needed
            os.makedirs(os.path.dirname(full_dest), exist_ok=True)
            shutil.copy2(full_source, full_dest)

            return {
                "success": True,
                "source_path": full_source,
                "dest_path": full_dest,
                "file_name": os.path.basename(full_dest)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_files(self, directory: str = "", pattern: str = "*") -> Dict[str, Any]:
        """List files in a directory"""
        full_path = os.path.join(self.workspace_dir, directory)

        # Validate
        is_valid, error_msg = self._validate_path(full_path)
        if not is_valid:
            return {"success": False, "error": error_msg}

        if not os.path.exists(full_path):
            return {"success": False, "error": "Directory not found"}

        try:
            files = []
            for item in Path(full_path).glob(pattern):
                if item.is_file():
                    files.append({
                        "name": item.name,
                        "path": str(item),
                        "size": item.stat().st_size,
                        "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                    })

            return {
                "success": True,
                "directory": full_path,
                "files": files,
                "count": len(files)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
