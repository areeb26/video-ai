"""
N8N Integration Service
Handles webhook triggers and workflow executions
"""
import httpx
from typing import Dict, Any, Optional
from datetime import datetime
from ..core.config import settings


class N8NIntegrationService:
    """Service for N8N workflow integration"""

    def __init__(self):
        self.webhook_url = settings.N8N_WEBHOOK_URL
        self.api_url = settings.N8N_API_URL
        self.api_key = settings.N8N_API_KEY

    async def trigger_webhook(
        self,
        webhook_path: str,
        payload: Dict[str, Any],
        method: str = "POST"
    ) -> Dict[str, Any]:
        """
        Trigger an N8N webhook

        Args:
            webhook_path: Webhook path (e.g., "my-workflow")
            payload: Data to send to the webhook
            method: HTTP method (POST, GET, etc.)

        Returns:
            Response from the webhook
        """
        url = f"{self.webhook_url}/{webhook_path}"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                if method.upper() == "POST":
                    response = await client.post(url, json=payload)
                elif method.upper() == "GET":
                    response = await client.get(url, params=payload)
                else:
                    return {"success": False, "error": f"Unsupported HTTP method: {method}"}

                response.raise_for_status()

                return {
                    "success": True,
                    "status_code": response.status_code,
                    "data": response.json() if response.text else None,
                    "execution_time": response.elapsed.total_seconds() * 1000
                }

        except httpx.TimeoutException:
            return {"success": False, "error": "Webhook request timed out"}
        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "error": f"HTTP error {e.response.status_code}",
                "status_code": e.response.status_code
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def execute_workflow(
        self,
        workflow_id: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute an N8N workflow via API

        Args:
            workflow_id: The N8N workflow ID
            data: Input data for the workflow

        Returns:
            Execution result
        """
        if not self.api_key:
            return {"success": False, "error": "N8N API key not configured"}

        url = f"{self.api_url}/workflows/{workflow_id}/execute"
        headers = {
            "X-N8N-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    url,
                    json={"data": data or {}},
                    headers=headers
                )
                response.raise_for_status()

                result = response.json()
                return {
                    "success": True,
                    "execution_id": result.get("id"),
                    "status": result.get("finished") and "success" or "running",
                    "data": result.get("data"),
                }

        except httpx.TimeoutException:
            return {"success": False, "error": "Workflow execution timed out"}
        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "error": f"HTTP error {e.response.status_code}",
                "details": e.response.text
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_workflow_status(self, execution_id: str) -> Dict[str, Any]:
        """
        Get the status of a workflow execution

        Args:
            execution_id: The execution ID

        Returns:
            Execution status
        """
        if not self.api_key:
            return {"success": False, "error": "N8N API key not configured"}

        url = f"{self.api_url}/executions/{execution_id}"
        headers = {"X-N8N-API-KEY": self.api_key}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()

                result = response.json()
                return {
                    "success": True,
                    "status": result.get("finished") and "completed" or "running",
                    "data": result.get("data"),
                    "started_at": result.get("startedAt"),
                    "finished_at": result.get("stoppedAt")
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def list_workflows(self) -> Dict[str, Any]:
        """
        List all available N8N workflows

        Returns:
            List of workflows
        """
        if not self.api_key:
            return {"success": False, "error": "N8N API key not configured"}

        url = f"{self.api_url}/workflows"
        headers = {"X-N8N-API-KEY": self.api_key}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()

                workflows = response.json()
                return {
                    "success": True,
                    "workflows": [
                        {
                            "id": w.get("id"),
                            "name": w.get("name"),
                            "active": w.get("active"),
                            "tags": w.get("tags", [])
                        }
                        for w in workflows.get("data", [])
                    ]
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_webhook_payload(
        self,
        event_type: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a standardized webhook payload

        Args:
            event_type: Type of event (task_created, file_created, etc.)
            data: Event data
            metadata: Additional metadata

        Returns:
            Formatted payload
        """
        return {
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "metadata": metadata or {},
            "source": "ai-assistant"
        }
