"""
N8N Workflow Model - Manages N8N workflow executions
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from ..core.database import Base


class N8NWorkflow(Base):
    """N8N workflow model for tracking workflow executions"""

    __tablename__ = "n8n_workflows"

    id = Column(Integer, primary_key=True, index=True)

    # Workflow identification
    workflow_id = Column(String(100), nullable=True)
    workflow_name = Column(String(200), nullable=False)
    webhook_url = Column(String(1000), nullable=False)

    # Execution details
    execution_id = Column(String(100), nullable=True)
    status = Column(String(50), default="pending")  # pending, running, success, failed

    # Request/Response
    request_payload = Column(JSON, nullable=True)
    response_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)

    # Timing
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    execution_time = Column(Integer, nullable=True)  # milliseconds

    # Context
    triggered_by = Column(String(200), nullable=True)  # task_id, command_id, manual
    language = Column(String(10), default="en")

    # Configuration
    auto_retry = Column(Boolean, default=False)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)

    def __repr__(self):
        return f"<N8NWorkflow {self.id}: {self.workflow_name} - {self.status}>"
