"""
WhatsApp Web Handler
Provides WhatsApp Web automation for the AI Assistant
"""
from .whatsapp_selenium import WhatsAppSelenium
from .whatsapp_simple import WhatsAppSimple
from .session_manager import SessionManager
from .message_queue import MessageQueue

__all__ = [
    "WhatsAppSelenium",
    "WhatsAppSimple",
    "SessionManager",
    "MessageQueue"
]
