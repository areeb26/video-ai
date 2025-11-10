"""
Main Assistant API - Natural Language Interface
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..schemas.assistant import AssistantRequest, AssistantResponse
from ..schemas.task import TaskCreate
from ..schemas.file_ops import FileOperationRequest
from ..modules.nlp_processor import BilingualNLPProcessor
from ..services.task_manager import TaskManager
from ..services.file_operations import FileOperationsService
from ..services.system_commands import SystemCommandsService
from ..services.n8n_integration import N8NIntegrationService

router = APIRouter(prefix="/assistant", tags=["assistant"])

# Initialize NLP processor
nlp = BilingualNLPProcessor()


@router.post("/", response_model=AssistantResponse)
async def process_command(request: AssistantRequest, db: Session = Depends(get_db)):
    """
    Process natural language command

    This is the main endpoint for interacting with the assistant
    in natural language (English or Urdu)
    """
    # Process the natural language input
    nlp_result = nlp.process(request.message, request.language)

    intent = nlp_result["intent"]
    entities = nlp_result["entities"]
    language = nlp_result["language"]
    extracted_data = nlp_result["extracted_data"]

    actions_taken = []
    response_message = ""
    success = True

    try:
        # Handle different intents
        if intent == "create_task":
            task_manager = TaskManager(db)
            task_data = TaskCreate(
                title=extracted_data or request.message,
                description=request.message,
                language=language,
                priority=entities.get("priority", "medium"),
                due_date=entities.get("due_date")
            )
            task = task_manager.create_task(task_data)
            actions_taken.append({
                "action": "task_created",
                "task_id": task.id,
                "title": task.title
            })
            response_message = nlp.generate_response("create_task", language)

        elif intent == "list_tasks":
            task_manager = TaskManager(db)
            tasks = task_manager.get_all_tasks(language=language)
            response_message = nlp.generate_response("list_tasks", language)
            actions_taken.append({
                "action": "tasks_listed",
                "count": len(tasks),
                "tasks": [{"id": t.id, "title": t.title, "status": t.status} for t in tasks]
            })

        elif intent == "complete_task":
            task_manager = TaskManager(db)
            # Try to find task by ID or title
            if extracted_data and extracted_data.isdigit():
                task = task_manager.complete_task(int(extracted_data))
            else:
                # Search by title (simplified - you might want fuzzy matching)
                tasks = task_manager.get_all_tasks()
                task = next((t for t in tasks if extracted_data.lower() in t.title.lower()), None)
                if task:
                    task = task_manager.complete_task(task.id)

            if task:
                response_message = nlp.generate_response("complete_task", language)
                actions_taken.append({"action": "task_completed", "task_id": task.id})
            else:
                success = False
                response_message = "Task not found" if language == "en" else "کام نہیں ملا"

        elif intent in ["file_create", "file_read", "file_edit"]:
            file_service = FileOperationsService()
            file_path = entities.get("file_path", extracted_data)

            if not file_path:
                success = False
                response_message = "File path not specified" if language == "en" else "فائل کا راستہ نہیں بتایا"
            else:
                if intent == "file_create":
                    result = file_service.create_file(file_path)
                    if result["success"]:
                        response_message = nlp.generate_response("file_create", language)
                        actions_taken.append({"action": "file_created", "path": result["file_path"]})
                    else:
                        success = False
                        response_message = result["error"]

                elif intent == "file_read":
                    result = file_service.read_file(file_path)
                    if result["success"]:
                        response_message = nlp.generate_response("file_read", language)
                        actions_taken.append({
                            "action": "file_read",
                            "path": result["file_path"],
                            "content": result["content"][:500]  # Preview
                        })
                    else:
                        success = False
                        response_message = result["error"]

        elif intent == "execute_command":
            cmd_service = SystemCommandsService()
            command = extracted_data

            if not command:
                success = False
                response_message = "Command not specified" if language == "en" else "کمانڈ نہیں بتائی"
            else:
                result = cmd_service.execute_command(command)
                if result["success"]:
                    response_message = nlp.generate_response("execute_command", language)
                    actions_taken.append({
                        "action": "command_executed",
                        "command": command,
                        "output": result["output"]
                    })
                else:
                    success = False
                    response_message = result["error"]

        elif intent == "trigger_n8n":
            n8n_service = N8NIntegrationService()
            workflow_name = extracted_data

            if not workflow_name:
                success = False
                response_message = "Workflow name not specified" if language == "en" else "ورک فلو کا نام نہیں بتایا"
            else:
                result = await n8n_service.trigger_webhook(
                    workflow_name,
                    {"message": request.message, "language": language}
                )
                if result["success"]:
                    response_message = nlp.generate_response("trigger_n8n", language)
                    actions_taken.append({
                        "action": "workflow_triggered",
                        "workflow": workflow_name
                    })
                else:
                    success = False
                    response_message = result["error"]

        else:
            response_message = nlp.generate_response("unknown", language)
            success = False

    except Exception as e:
        success = False
        response_message = nlp.generate_response("error", language).format(error=str(e))

    return AssistantResponse(
        message=response_message,
        language=language,
        intent=intent,
        entities=entities,
        actions=actions_taken,
        success=success,
        metadata={
            "confidence": nlp_result["confidence"],
            "detected_language": nlp_result["detected_language"]
        }
    )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Multitask Assistant",
        "nlp": "operational"
    }
