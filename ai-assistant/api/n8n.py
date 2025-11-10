"""
N8N Workflow API endpoints
"""
from fastapi import APIRouter, HTTPException
from ..schemas.n8n import N8NWorkflowRequest, N8NWorkflowResponse
from ..services.n8n_integration import N8NIntegrationService

router = APIRouter(prefix="/n8n", tags=["n8n"])

n8n_service = N8NIntegrationService()


@router.post("/trigger")
async def trigger_webhook(request: N8NWorkflowRequest):
    """Trigger an N8N webhook"""
    result = await n8n_service.trigger_webhook(
        request.workflow_name,
        request.payload or {}
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    return {
        "success": True,
        "workflow_name": request.workflow_name,
        "status": result.get("status_code"),
        "data": result.get("data"),
        "execution_time": result.get("execution_time")
    }


@router.post("/execute/{workflow_id}")
async def execute_workflow(workflow_id: str, request: N8NWorkflowRequest):
    """Execute an N8N workflow by ID"""
    result = await n8n_service.execute_workflow(
        workflow_id,
        request.payload
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.get("/status/{execution_id}")
async def get_workflow_status(execution_id: str):
    """Get workflow execution status"""
    result = await n8n_service.get_workflow_status(execution_id)

    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


@router.get("/workflows")
async def list_workflows():
    """List all available workflows"""
    result = await n8n_service.list_workflows()

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])

    return result
