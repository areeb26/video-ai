"""
Simple WhatsApp automation using PyWhatKit
Good for sending messages only, no receiving capability
"""
import logging
from typing import Optional
from datetime import datetime, timedelta
import pywhatkit as pwk
from .utils import format_phone_number, sanitize_message

logger = logging.getLogger(__name__)


class WhatsAppSimple:
    """Simple WhatsApp sender using PyWhatKit"""

    def __init__(self):
        """Initialize WhatsApp Simple handler"""
        logger.info("WhatsApp Simple initialized")

    def send_message_now(
        self,
        number: str,
        message: str,
        wait_time: int = 15,
        close_tab: bool = True
    ) -> bool:
        """
        Send message immediately

        Args:
            number: Phone number
            message: Message to send
            wait_time: Time to wait before closing tab (seconds)
            close_tab: Close tab after sending

        Returns:
            True if successful
        """
        try:
            # Format phone number
            formatted_number = format_phone_number(number)

            # Sanitize message
            message = sanitize_message(message)

            # Send message
            pwk.sendwhatmsg_instantly(
                phone_no=formatted_number,
                message=message,
                wait_time=wait_time,
                tab_close=close_tab
            )

            logger.info(f"Message sent to {number}")
            return True

        except Exception as e:
            logger.error(f"Failed to send message to {number}: {e}")
            return False

    def send_message_at(
        self,
        number: str,
        message: str,
        hour: int,
        minute: int,
        close_tab: bool = True
    ) -> bool:
        """
        Schedule message for specific time today

        Args:
            number: Phone number
            message: Message to send
            hour: Hour (24-hour format)
            minute: Minute
            close_tab: Close tab after sending

        Returns:
            True if scheduled successfully
        """
        try:
            # Format phone number
            formatted_number = format_phone_number(number)

            # Sanitize message
            message = sanitize_message(message)

            # Send message at specific time
            pwk.sendwhatmsg(
                phone_no=formatted_number,
                message=message,
                time_hour=hour,
                time_min=minute,
                tab_close=close_tab
            )

            logger.info(f"Message scheduled for {hour}:{minute:02d} to {number}")
            return True

        except Exception as e:
            logger.error(f"Failed to schedule message to {number}: {e}")
            return False

    def send_message_after(
        self,
        number: str,
        message: str,
        minutes: int = 1,
        close_tab: bool = True
    ) -> bool:
        """
        Send message after specified minutes

        Args:
            number: Phone number
            message: Message to send
            minutes: Minutes to wait
            close_tab: Close tab after sending

        Returns:
            True if scheduled successfully
        """
        try:
            # Calculate target time
            target_time = datetime.now() + timedelta(minutes=minutes)
            hour = target_time.hour
            minute = target_time.minute

            return self.send_message_at(
                number=number,
                message=message,
                hour=hour,
                minute=minute,
                close_tab=close_tab
            )

        except Exception as e:
            logger.error(f"Failed to schedule message: {e}")
            return False

    def send_to_group(
        self,
        group_id: str,
        message: str,
        close_tab: bool = True
    ) -> bool:
        """
        Send message to WhatsApp group

        Args:
            group_id: Group ID (from group invite link)
            message: Message to send
            close_tab: Close tab after sending

        Returns:
            True if successful
        """
        try:
            # Sanitize message
            message = sanitize_message(message)

            # Send to group
            pwk.sendwhatmsg_to_group_instantly(
                group_id=group_id,
                message=message,
                tab_close=close_tab
            )

            logger.info(f"Message sent to group {group_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to send to group {group_id}: {e}")
            return False

    def send_image(
        self,
        number: str,
        image_path: str,
        caption: str = "",
        wait_time: int = 15
    ) -> bool:
        """
        Send image to phone number

        Args:
            number: Phone number
            image_path: Path to image file
            caption: Image caption
            wait_time: Wait time before closing

        Returns:
            True if successful
        """
        try:
            # Format phone number
            formatted_number = format_phone_number(number)

            # Sanitize caption
            caption = sanitize_message(caption) if caption else ""

            # Send image
            pwk.sendwhats_image(
                receiver=formatted_number,
                img_path=image_path,
                caption=caption,
                wait_time=wait_time
            )

            logger.info(f"Image sent to {number}")
            return True

        except Exception as e:
            logger.error(f"Failed to send image to {number}: {e}")
            return False

    @staticmethod
    def get_info() -> dict:
        """
        Get PyWhatKit information

        Returns:
            Dictionary with library info
        """
        return {
            "library": "pywhatkit",
            "capabilities": [
                "Send instant messages",
                "Schedule messages",
                "Send to groups",
                "Send images"
            ],
            "limitations": [
                "Cannot receive messages",
                "Requires browser automation",
                "No session persistence",
                "Opens new tab each time"
            ],
            "best_for": [
                "Simple notifications",
                "Scheduled reminders",
                "One-way communication"
            ]
        }
