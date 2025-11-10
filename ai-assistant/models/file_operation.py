"""
File Operation Model - Tracks file operations performed by the assistant
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, BigInteger
from sqlalchemy.sql import func
from ..core.database import Base


class FileOperation(Base):
    """File operations model for tracking file manipulations"""

    __tablename__ = "file_operations"

    id = Column(Integer, primary_key=True, index=True)

    # Operation details
    operation_type = Column(String(50), nullable=False)  # create, read, edit, delete, move, copy
    file_path = Column(String(1000), nullable=False)
    new_path = Column(String(1000), nullable=True)  # For move/copy operations

    # File details
    file_name = Column(String(500), nullable=False)
    file_extension = Column(String(50), nullable=True)
    file_size = Column(BigInteger, nullable=True)  # bytes

    # Content tracking
    content_preview = Column(Text, nullable=True)  # First 500 chars

    # Status
    status = Column(String(50), default="pending")  # pending, success, failed
    error_message = Column(Text, nullable=True)

    # Timing
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Context
    user_command = Column(Text, nullable=True)
    language = Column(String(10), default="en")

    def __repr__(self):
        return f"<FileOperation {self.id}: {self.operation_type} - {self.file_name}>"
