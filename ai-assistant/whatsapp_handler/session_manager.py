"""
Session Manager for WhatsApp Web
Handles persistent sessions and reconnection
"""
import os
import json
import time
import logging
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class SessionManager:
    """Manage WhatsApp Web sessions"""

    def __init__(self, session_dir: str = None):
        """
        Initialize Session Manager

        Args:
            session_dir: Directory for session data
        """
        self.session_dir = session_dir or os.path.join(
            os.path.expanduser("~"),
            ".ai-assistant",
            "whatsapp-session"
        )

        self.metadata_file = os.path.join(self.session_dir, "session_metadata.json")
        self.authorized_numbers_file = os.path.join(
            self.session_dir,
            "authorized_numbers.json"
        )

        # Create session directory
        os.makedirs(self.session_dir, exist_ok=True)

        logger.info(f"Session Manager initialized: {self.session_dir}")

    def save_session_metadata(self, metadata: Dict[str, Any]) -> bool:
        """
        Save session metadata

        Args:
            metadata: Session metadata dictionary

        Returns:
            True if saved successfully
        """
        try:
            metadata['last_updated'] = datetime.now().isoformat()

            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)

            logger.info("Session metadata saved")
            return True

        except Exception as e:
            logger.error(f"Failed to save session metadata: {e}")
            return False

    def load_session_metadata(self) -> Optional[Dict[str, Any]]:
        """
        Load session metadata

        Returns:
            Metadata dictionary or None
        """
        try:
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, 'r') as f:
                    metadata = json.load(f)

                logger.info("Session metadata loaded")
                return metadata

            return None

        except Exception as e:
            logger.error(f"Failed to load session metadata: {e}")
            return None

    def is_session_valid(self, max_age_hours: int = 720) -> bool:
        """
        Check if session is still valid

        Args:
            max_age_hours: Maximum age of session in hours (default: 30 days)

        Returns:
            True if session is valid
        """
        try:
            metadata = self.load_session_metadata()

            if not metadata:
                return False

            # Check last updated time
            last_updated = datetime.fromisoformat(metadata.get('last_updated', ''))
            age_hours = (datetime.now() - last_updated).total_seconds() / 3600

            if age_hours > max_age_hours:
                logger.warning(f"Session expired (age: {age_hours:.1f} hours)")
                return False

            return True

        except Exception as e:
            logger.error(f"Failed to check session validity: {e}")
            return False

    def update_session_activity(self) -> bool:
        """
        Update session last activity timestamp

        Returns:
            True if updated successfully
        """
        try:
            metadata = self.load_session_metadata() or {}
            metadata['last_activity'] = datetime.now().isoformat()

            return self.save_session_metadata(metadata)

        except Exception as e:
            logger.error(f"Failed to update session activity: {e}")
            return False

    def save_authorized_numbers(self, numbers: list) -> bool:
        """
        Save list of authorized numbers

        Args:
            numbers: List of authorized phone numbers

        Returns:
            True if saved successfully
        """
        try:
            data = {
                'authorized_numbers': numbers,
                'updated_at': datetime.now().isoformat()
            }

            with open(self.authorized_numbers_file, 'w') as f:
                json.dump(data, f, indent=2)

            logger.info(f"Authorized numbers saved ({len(numbers)} numbers)")
            return True

        except Exception as e:
            logger.error(f"Failed to save authorized numbers: {e}")
            return False

    def load_authorized_numbers(self) -> list:
        """
        Load list of authorized numbers

        Returns:
            List of authorized phone numbers
        """
        try:
            if os.path.exists(self.authorized_numbers_file):
                with open(self.authorized_numbers_file, 'r') as f:
                    data = json.load(f)

                return data.get('authorized_numbers', [])

            return []

        except Exception as e:
            logger.error(f"Failed to load authorized numbers: {e}")
            return []

    def add_authorized_number(self, number: str) -> bool:
        """
        Add a number to authorized list

        Args:
            number: Phone number to authorize

        Returns:
            True if added successfully
        """
        try:
            numbers = self.load_authorized_numbers()

            if number not in numbers:
                numbers.append(number)
                return self.save_authorized_numbers(numbers)

            return True

        except Exception as e:
            logger.error(f"Failed to add authorized number: {e}")
            return False

    def remove_authorized_number(self, number: str) -> bool:
        """
        Remove a number from authorized list

        Args:
            number: Phone number to remove

        Returns:
            True if removed successfully
        """
        try:
            numbers = self.load_authorized_numbers()

            if number in numbers:
                numbers.remove(number)
                return self.save_authorized_numbers(numbers)

            return True

        except Exception as e:
            logger.error(f"Failed to remove authorized number: {e}")
            return False

    def is_number_authorized(self, number: str) -> bool:
        """
        Check if a number is authorized

        Args:
            number: Phone number to check

        Returns:
            True if authorized
        """
        from .utils import format_phone_number

        formatted_number = format_phone_number(number)
        authorized_numbers = self.load_authorized_numbers()

        for auth_number in authorized_numbers:
            if format_phone_number(auth_number) == formatted_number:
                return True

        return False

    def get_session_stats(self) -> Dict[str, Any]:
        """
        Get session statistics

        Returns:
            Dictionary with session stats
        """
        metadata = self.load_session_metadata() or {}

        return {
            'session_exists': os.path.exists(self.metadata_file),
            'session_dir': self.session_dir,
            'last_updated': metadata.get('last_updated'),
            'last_activity': metadata.get('last_activity'),
            'is_valid': self.is_session_valid(),
            'authorized_count': len(self.load_authorized_numbers())
        }

    def clear_session(self) -> bool:
        """
        Clear session data

        Returns:
            True if cleared successfully
        """
        try:
            # Remove metadata file
            if os.path.exists(self.metadata_file):
                os.remove(self.metadata_file)

            logger.info("Session cleared")
            return True

        except Exception as e:
            logger.error(f"Failed to clear session: {e}")
            return False

    def backup_session(self, backup_dir: str = None) -> bool:
        """
        Backup session data

        Args:
            backup_dir: Directory for backup (default: session_dir/backups)

        Returns:
            True if backed up successfully
        """
        try:
            import shutil

            backup_dir = backup_dir or os.path.join(self.session_dir, "backups")
            os.makedirs(backup_dir, exist_ok=True)

            # Create backup with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(backup_dir, f"session_backup_{timestamp}")

            # Copy session directory
            shutil.copytree(self.session_dir, backup_path, dirs_exist_ok=True)

            logger.info(f"Session backed up to: {backup_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to backup session: {e}")
            return False
