"""
Message Queue for scheduled WhatsApp messages
"""
import json
import logging
import time
import threading
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
import os

logger = logging.getLogger(__name__)


class MessageQueue:
    """Queue system for scheduled WhatsApp messages"""

    def __init__(self, queue_file: str = None):
        """
        Initialize Message Queue

        Args:
            queue_file: Path to queue storage file
        """
        self.queue_file = queue_file or os.path.join(
            os.path.expanduser("~"),
            ".ai-assistant",
            "whatsapp-queue.json"
        )

        # Create directory if needed
        os.makedirs(os.path.dirname(self.queue_file), exist_ok=True)

        self.queue: List[Dict[str, Any]] = []
        self.running = False
        self.worker_thread: Optional[threading.Thread] = None

        # Load existing queue
        self.load_queue()

        logger.info(f"Message Queue initialized: {self.queue_file}")

    def add_message(
        self,
        number: str,
        message: str,
        send_at: datetime,
        message_type: str = "text",
        **kwargs
    ) -> str:
        """
        Add message to queue

        Args:
            number: Phone number
            message: Message content
            send_at: When to send the message
            message_type: Type (text, image, file)
            **kwargs: Additional parameters

        Returns:
            Message ID
        """
        import uuid

        message_id = str(uuid.uuid4())

        queue_item = {
            'id': message_id,
            'number': number,
            'message': message,
            'send_at': send_at.isoformat(),
            'type': message_type,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'attempts': 0,
            'extra': kwargs
        }

        self.queue.append(queue_item)
        self.save_queue()

        logger.info(f"Message queued: {message_id} for {send_at}")
        return message_id

    def schedule_message(
        self,
        number: str,
        message: str,
        delay_minutes: int = 0,
        delay_hours: int = 0,
        delay_days: int = 0,
        **kwargs
    ) -> str:
        """
        Schedule message with relative delay

        Args:
            number: Phone number
            message: Message content
            delay_minutes: Delay in minutes
            delay_hours: Delay in hours
            delay_days: Delay in days
            **kwargs: Additional parameters

        Returns:
            Message ID
        """
        send_at = datetime.now() + timedelta(
            minutes=delay_minutes,
            hours=delay_hours,
            days=delay_days
        )

        return self.add_message(number, message, send_at, **kwargs)

    def get_pending_messages(self) -> List[Dict[str, Any]]:
        """
        Get messages that should be sent now

        Returns:
            List of pending messages
        """
        now = datetime.now()
        pending = []

        for msg in self.queue:
            if msg['status'] == 'pending':
                send_at = datetime.fromisoformat(msg['send_at'])
                if send_at <= now:
                    pending.append(msg)

        return pending

    def mark_sent(self, message_id: str) -> bool:
        """
        Mark message as sent

        Args:
            message_id: Message ID

        Returns:
            True if marked successfully
        """
        for msg in self.queue:
            if msg['id'] == message_id:
                msg['status'] = 'sent'
                msg['sent_at'] = datetime.now().isoformat()
                self.save_queue()
                logger.info(f"Message marked as sent: {message_id}")
                return True

        return False

    def mark_failed(self, message_id: str, error: str = "") -> bool:
        """
        Mark message as failed

        Args:
            message_id: Message ID
            error: Error message

        Returns:
            True if marked successfully
        """
        for msg in self.queue:
            if msg['id'] == message_id:
                msg['status'] = 'failed'
                msg['error'] = error
                msg['failed_at'] = datetime.now().isoformat()
                msg['attempts'] = msg.get('attempts', 0) + 1

                # Retry logic: reschedule if attempts < 3
                if msg['attempts'] < 3:
                    # Reschedule for 5 minutes later
                    new_send_at = datetime.now() + timedelta(minutes=5)
                    msg['send_at'] = new_send_at.isoformat()
                    msg['status'] = 'pending'
                    logger.info(f"Message rescheduled: {message_id} (attempt {msg['attempts']})")

                self.save_queue()
                return True

        return False

    def cancel_message(self, message_id: str) -> bool:
        """
        Cancel a scheduled message

        Args:
            message_id: Message ID

        Returns:
            True if cancelled successfully
        """
        for msg in self.queue:
            if msg['id'] == message_id and msg['status'] == 'pending':
                msg['status'] = 'cancelled'
                msg['cancelled_at'] = datetime.now().isoformat()
                self.save_queue()
                logger.info(f"Message cancelled: {message_id}")
                return True

        return False

    def get_message(self, message_id: str) -> Optional[Dict[str, Any]]:
        """
        Get message by ID

        Args:
            message_id: Message ID

        Returns:
            Message dictionary or None
        """
        for msg in self.queue:
            if msg['id'] == message_id:
                return msg

        return None

    def get_all_messages(self, status: str = None) -> List[Dict[str, Any]]:
        """
        Get all messages, optionally filtered by status

        Args:
            status: Filter by status (pending, sent, failed, cancelled)

        Returns:
            List of messages
        """
        if status:
            return [msg for msg in self.queue if msg['status'] == status]

        return self.queue.copy()

    def cleanup_old_messages(self, days: int = 7) -> int:
        """
        Remove old sent/failed messages

        Args:
            days: Remove messages older than this many days

        Returns:
            Number of messages removed
        """
        cutoff = datetime.now() - timedelta(days=days)
        original_count = len(self.queue)

        self.queue = [
            msg for msg in self.queue
            if msg['status'] == 'pending' or
            datetime.fromisoformat(msg.get('created_at', '9999-12-31')) > cutoff
        ]

        removed = original_count - len(self.queue)

        if removed > 0:
            self.save_queue()
            logger.info(f"Cleaned up {removed} old messages")

        return removed

    def save_queue(self) -> bool:
        """
        Save queue to file

        Returns:
            True if saved successfully
        """
        try:
            with open(self.queue_file, 'w') as f:
                json.dump(self.queue, f, indent=2)

            return True

        except Exception as e:
            logger.error(f"Failed to save queue: {e}")
            return False

    def load_queue(self) -> bool:
        """
        Load queue from file

        Returns:
            True if loaded successfully
        """
        try:
            if os.path.exists(self.queue_file):
                with open(self.queue_file, 'r') as f:
                    self.queue = json.load(f)

                logger.info(f"Queue loaded: {len(self.queue)} messages")
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to load queue: {e}")
            return False

    def start_worker(self, whatsapp_handler, check_interval: int = 30):
        """
        Start background worker to process queue

        Args:
            whatsapp_handler: WhatsApp handler instance
            check_interval: Check interval in seconds
        """
        if self.running:
            logger.warning("Worker already running")
            return

        self.running = True

        def worker():
            logger.info("Message queue worker started")

            while self.running:
                try:
                    # Get pending messages
                    pending = self.get_pending_messages()

                    for msg in pending:
                        try:
                            # Send message
                            if msg['type'] == 'text':
                                success = whatsapp_handler.send_message(
                                    msg['number'],
                                    msg['message']
                                )
                            elif msg['type'] == 'file':
                                success = whatsapp_handler.send_file(
                                    msg['number'],
                                    msg['extra'].get('file_path'),
                                    msg.get('message', '')
                                )
                            else:
                                success = False

                            # Update status
                            if success:
                                self.mark_sent(msg['id'])
                            else:
                                self.mark_failed(msg['id'], "Send failed")

                        except Exception as e:
                            logger.error(f"Error sending message {msg['id']}: {e}")
                            self.mark_failed(msg['id'], str(e))

                    # Wait before next check
                    time.sleep(check_interval)

                except Exception as e:
                    logger.error(f"Worker error: {e}")
                    time.sleep(check_interval)

            logger.info("Message queue worker stopped")

        self.worker_thread = threading.Thread(target=worker, daemon=True)
        self.worker_thread.start()

    def stop_worker(self):
        """Stop background worker"""
        if self.running:
            self.running = False
            if self.worker_thread:
                self.worker_thread.join(timeout=5)

            logger.info("Worker stopped")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get queue statistics

        Returns:
            Statistics dictionary
        """
        return {
            'total': len(self.queue),
            'pending': len([m for m in self.queue if m['status'] == 'pending']),
            'sent': len([m for m in self.queue if m['status'] == 'sent']),
            'failed': len([m for m in self.queue if m['status'] == 'failed']),
            'cancelled': len([m for m in self.queue if m['status'] == 'cancelled']),
        }
