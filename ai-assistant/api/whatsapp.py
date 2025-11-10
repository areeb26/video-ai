"""
WhatsApp API endpoints
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
import logging
from ..schemas.whatsapp import (
    WhatsAppMessageRequest,
    WhatsAppFileRequest,
    WhatsAppScheduleRequest,
    WhatsAppMessageResponse,
    WhatsAppAuthRequest,
    WhatsAppSessionResponse
)
from ..whatsapp_handler import (
    WhatsAppSelenium,
    WhatsAppSimple,
    SessionManager,
    MessageQueue
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])

# Global instances (will be initialized on startup)
whatsapp_selenium: WhatsAppSelenium = None
whatsapp_simple: WhatsAppSimple = None
session_manager: SessionManager = None
message_queue: MessageQueue = None


def get_whatsapp_handler(method: str = "selenium"):
    """Get WhatsApp handler instance"""
    if method == "simple":
        return whatsapp_simple
    return whatsapp_selenium


@router.on_event("startup")
async def startup_whatsapp():
    """Initialize WhatsApp handlers on startup"""
    global whatsapp_selenium, whatsapp_simple, session_manager, message_queue

    try:
        # Initialize handlers
        whatsapp_simple = WhatsAppSimple()
        session_manager = SessionManager()
        message_queue = MessageQueue()

        # Initialize Selenium (don't wait for login on startup)
        whatsapp_selenium = WhatsAppSelenium()

        logger.info("WhatsApp handlers initialized")

    except Exception as e:
        logger.error(f"Failed to initialize WhatsApp handlers: {e}")


@router.post("/initialize")
async def initialize_whatsapp(background_tasks: BackgroundTasks):
    """
    Initialize WhatsApp Web with QR code scan
    This should be called once to setup the session
    """
    try:
        if not whatsapp_selenium:
            raise HTTPException(status_code=500, detail="WhatsApp handler not initialized")

        # Initialize in background to not block
        def init_task():
            success = whatsapp_selenium.initialize(wait_for_login=True, timeout=120)
            if success:
                session_manager.save_session_metadata({
                    'initialized': True,
                    'method': 'selenium'
                })

        background_tasks.add_task(init_task)

        return {
            "message": "WhatsApp initialization started. Please scan QR code.",
            "instructions": "Open WhatsApp on your phone and scan the QR code in the browser window."
        }

    except Exception as e:
        logger.error(f"Failed to initialize WhatsApp: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send", response_model=WhatsAppMessageResponse)
async def send_message(request: WhatsAppMessageRequest):
    """Send WhatsApp message"""
    try:
        handler = get_whatsapp_handler(request.method)

        if request.method == "selenium":
            if not whatsapp_selenium.is_logged_in:
                raise HTTPException(
                    status_code=400,
                    detail="Not logged in to WhatsApp. Please initialize first."
                )

            # Check if number is authorized
            if not session_manager.is_number_authorized(request.number):
                logger.warning(f"Unauthorized number attempted: {request.number}")
                # You can either block or allow - here we'll allow but log
                # raise HTTPException(status_code=403, detail="Number not authorized")

            success = whatsapp_selenium.send_message(request.number, request.message)

        else:  # simple method
            success = whatsapp_simple.send_message_now(request.number, request.message)

        if success:
            return WhatsAppMessageResponse(
                success=True,
                message="Message sent successfully"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to send message")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-file", response_model=WhatsAppMessageResponse)
async def send_file(request: WhatsAppFileRequest):
    """Send file via WhatsApp"""
    try:
        if not whatsapp_selenium.is_logged_in:
            raise HTTPException(
                status_code=400,
                detail="Not logged in to WhatsApp. Please initialize first."
            )

        success = whatsapp_selenium.send_file(
            request.number,
            request.file_path,
            request.caption
        )

        if success:
            return WhatsAppMessageResponse(
                success=True,
                message="File sent successfully"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to send file")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/schedule", response_model=WhatsAppMessageResponse)
async def schedule_message(request: WhatsAppScheduleRequest):
    """Schedule WhatsApp message"""
    try:
        if request.send_at:
            message_id = message_queue.add_message(
                request.number,
                request.message,
                request.send_at
            )
        else:
            message_id = message_queue.schedule_message(
                request.number,
                request.message,
                delay_minutes=request.delay_minutes,
                delay_hours=request.delay_hours,
                delay_days=request.delay_days
            )

        return WhatsAppMessageResponse(
            success=True,
            message="Message scheduled successfully",
            message_id=message_id
        )

    except Exception as e:
        logger.error(f"Error scheduling message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queue/pending")
async def get_pending_messages():
    """Get pending messages in queue"""
    try:
        pending = message_queue.get_pending_messages()
        return {
            "count": len(pending),
            "messages": pending
        }

    except Exception as e:
        logger.error(f"Error getting pending messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/queue/{message_id}")
async def cancel_message(message_id: str):
    """Cancel scheduled message"""
    try:
        success = message_queue.cancel_message(message_id)

        if success:
            return {"message": "Message cancelled successfully"}
        else:
            raise HTTPException(status_code=404, detail="Message not found or already sent")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queue/stats")
async def get_queue_stats():
    """Get message queue statistics"""
    try:
        return message_queue.get_stats()

    except Exception as e:
        logger.error(f"Error getting queue stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/authorize")
async def authorize_number(request: WhatsAppAuthRequest):
    """Add authorized number"""
    try:
        success = session_manager.add_authorized_number(request.number)

        if success:
            return {"message": f"Number {request.number} authorized successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to authorize number")

    except Exception as e:
        logger.error(f"Error authorizing number: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/authorize/{number}")
async def deauthorize_number(number: str):
    """Remove authorized number"""
    try:
        success = session_manager.remove_authorized_number(number)

        if success:
            return {"message": f"Number {number} removed from authorized list"}
        else:
            raise HTTPException(status_code=404, detail="Number not found")

    except Exception as e:
        logger.error(f"Error deauthorizing number: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/authorized")
async def list_authorized_numbers():
    """List all authorized numbers"""
    try:
        numbers = session_manager.load_authorized_numbers()
        return {
            "count": len(numbers),
            "numbers": numbers
        }

    except Exception as e:
        logger.error(f"Error listing authorized numbers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=WhatsAppSessionResponse)
async def get_status():
    """Get WhatsApp session status"""
    try:
        is_logged_in = whatsapp_selenium.is_logged_in if whatsapp_selenium else False
        session_valid = session_manager.is_session_valid()
        session_stats = session_manager.get_session_stats()
        queue_stats = message_queue.get_stats()

        return WhatsAppSessionResponse(
            is_logged_in=is_logged_in,
            session_valid=session_valid,
            session_stats=session_stats,
            queue_stats=queue_stats
        )

    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/health-check")
async def health_check():
    """Check WhatsApp connection health"""
    try:
        if not whatsapp_selenium:
            return {"healthy": False, "message": "WhatsApp not initialized"}

        healthy = whatsapp_selenium.health_check()

        return {
            "healthy": healthy,
            "message": "Connection healthy" if healthy else "Connection issues detected"
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"healthy": False, "message": str(e)}


@router.post("/reconnect")
async def reconnect():
    """Attempt to reconnect to WhatsApp"""
    try:
        if not whatsapp_selenium:
            raise HTTPException(status_code=500, detail="WhatsApp not initialized")

        success = whatsapp_selenium.reconnect()

        if success:
            return {"message": "Reconnected successfully"}
        else:
            raise HTTPException(status_code=500, detail="Reconnection failed")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reconnection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start-queue-worker")
async def start_queue_worker():
    """Start the message queue worker"""
    try:
        if not whatsapp_selenium:
            raise HTTPException(status_code=500, detail="WhatsApp not initialized")

        message_queue.start_worker(whatsapp_selenium, check_interval=30)

        return {"message": "Queue worker started"}

    except Exception as e:
        logger.error(f"Error starting queue worker: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop-queue-worker")
async def stop_queue_worker():
    """Stop the message queue worker"""
    try:
        message_queue.stop_worker()
        return {"message": "Queue worker stopped"}

    except Exception as e:
        logger.error(f"Error stopping queue worker: {e}")
        raise HTTPException(status_code=500, detail=str(e))
