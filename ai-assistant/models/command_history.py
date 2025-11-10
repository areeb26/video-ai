"""
Command History Model - Tracks all executed commands
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from ..core.database import Base


class CommandHistory(Base):
    """Command history model for tracking executed commands"""

    __tablename__ = "command_history"

    id = Column(Integer, primary_key=True, index=True)

    # Command details
    command = Column(Text, nullable=False)
    command_type = Column(String(50), nullable=False)  # system, file, n8n, task, etc.
    language = Column(String(10), default="en")  # Language of the command

    # Execution details
    status = Column(String(50), default="pending")  # pending, success, failed, blocked
    output = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)

    # Safety
    is_safe = Column(Boolean, default=True)
    was_blocked = Column(Boolean, default=False)

    # Timing
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    executed_at = Column(DateTime(timezone=True), nullable=True)
    execution_time = Column(Integer, nullable=True)  # milliseconds

    # Context
    user_input = Column(Text, nullable=True)  # Original user input
    parsed_intent = Column(String(200), nullable=True)

    def __repr__(self):
        return f"<CommandHistory {self.id}: {self.command_type} - {self.status}>"
