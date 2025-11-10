"""
WhatsApp Web Automation using Selenium
Full-featured implementation with send/receive capabilities
"""
import os
import time
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException
)
from .utils import format_phone_number, sanitize_message, detect_language_from_message

logger = logging.getLogger(__name__)


class WhatsAppSelenium:
    """WhatsApp Web automation using Selenium WebDriver"""

    def __init__(self, session_dir: str = None, headless: bool = False):
        """
        Initialize WhatsApp Selenium handler

        Args:
            session_dir: Directory to store Chrome session data
            headless: Run browser in headless mode
        """
        self.session_dir = session_dir or os.path.join(
            os.path.expanduser("~"),
            ".ai-assistant",
            "whatsapp-session"
        )
        self.headless = headless
        self.driver: Optional[webdriver.Chrome] = None
        self.is_logged_in = False
        self.last_health_check = time.time()

        # Create session directory
        os.makedirs(self.session_dir, exist_ok=True)

        logger.info(f"WhatsApp Selenium initialized. Session dir: {self.session_dir}")

    def initialize(self, wait_for_login: bool = True, timeout: int = 60) -> bool:
        """
        Initialize WhatsApp Web

        Args:
            wait_for_login: Wait for QR code scan
            timeout: Maximum time to wait for login (seconds)

        Returns:
            True if initialized successfully
        """
        try:
            # Setup Chrome options
            chrome_options = Options()

            # Use persistent session
            chrome_options.add_argument(f"user-data-dir={self.session_dir}")
            chrome_options.add_argument("--profile-directory=Default")

            # Additional options
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")

            # User agent to avoid detection
            chrome_options.add_argument(
                "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )

            if self.headless:
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--window-size=1920,1080")

            # Disable notifications
            prefs = {
                "profile.default_content_setting_values.notifications": 2
            }
            chrome_options.add_experimental_option("prefs", prefs)

            # Initialize driver
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.get("https://web.whatsapp.com")

            logger.info("WhatsApp Web opened")

            if wait_for_login:
                return self._wait_for_login(timeout)

            return True

        except Exception as e:
            logger.error(f"Failed to initialize WhatsApp: {e}")
            return False

    def _wait_for_login(self, timeout: int = 60) -> bool:
        """
        Wait for user to scan QR code and login

        Args:
            timeout: Maximum wait time in seconds

        Returns:
            True if logged in successfully
        """
        try:
            logger.info("Waiting for QR code scan...")
            print("\n" + "="*50)
            print("Please scan the QR code with your phone")
            print("="*50 + "\n")

            # Wait for QR code to appear
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "canvas"))
            )
            logger.info("QR code displayed. Scan with your phone...")

            # Wait for login (QR code disappears and chat loads)
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div[data-testid='chat-list']")
                )
            )

            self.is_logged_in = True
            logger.info("Login successful!")
            print("\n✅ Login successful!\n")

            return True

        except TimeoutException:
            logger.error("Login timeout - QR code not scanned in time")
            print("\n❌ Login timeout. Please try again.\n")
            return False
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False

    def send_message(
        self,
        number: str,
        message: str,
        wait_time: int = 10
    ) -> bool:
        """
        Send message to a phone number

        Args:
            number: Phone number (with or without country code)
            message: Message to send
            wait_time: Time to wait for chat to load

        Returns:
            True if message sent successfully
        """
        if not self.is_logged_in:
            logger.error("Not logged in to WhatsApp")
            return False

        try:
            # Format phone number
            formatted_number = format_phone_number(number).replace('+', '')

            # Sanitize message
            message = sanitize_message(message)

            # Open chat using URL
            url = f"https://web.whatsapp.com/send?phone={formatted_number}"
            self.driver.get(url)

            # Wait for chat to load
            WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div[contenteditable='true'][data-tab='10']")
                )
            )

            # Find message input box
            message_box = self.driver.find_element(
                By.CSS_SELECTOR,
                "div[contenteditable='true'][data-tab='10']"
            )

            # Type message (handle multi-line)
            lines = message.split('\n')
            for i, line in enumerate(lines):
                message_box.send_keys(line)
                if i < len(lines) - 1:
                    message_box.send_keys(Keys.SHIFT + Keys.ENTER)

            time.sleep(0.5)  # Small delay before sending

            # Send message
            message_box.send_keys(Keys.ENTER)

            logger.info(f"Message sent to {number}")
            return True

        except TimeoutException:
            logger.error(f"Timeout waiting for chat to load: {number}")
            return False
        except Exception as e:
            logger.error(f"Failed to send message to {number}: {e}")
            return False

    def send_file(
        self,
        number: str,
        file_path: str,
        caption: str = "",
        wait_time: int = 10
    ) -> bool:
        """
        Send file to a phone number

        Args:
            number: Phone number
            file_path: Path to file
            caption: Optional caption
            wait_time: Wait time for upload

        Returns:
            True if file sent successfully
        """
        if not self.is_logged_in:
            logger.error("Not logged in to WhatsApp")
            return False

        try:
            # Check if file exists
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return False

            # Format phone number
            formatted_number = format_phone_number(number).replace('+', '')

            # Open chat
            url = f"https://web.whatsapp.com/send?phone={formatted_number}"
            self.driver.get(url)

            # Wait for chat to load
            WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div[contenteditable='true'][data-tab='10']")
                )
            )

            # Click attach button
            attach_btn = self.driver.find_element(
                By.CSS_SELECTOR,
                "div[title='Attach']"
            )
            attach_btn.click()

            time.sleep(0.5)

            # Click document/image option
            file_input = self.driver.find_element(
                By.CSS_SELECTOR,
                "input[type='file']"
            )

            # Upload file
            file_input.send_keys(os.path.abspath(file_path))

            # Wait for preview
            time.sleep(2)

            # Add caption if provided
            if caption:
                caption_box = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "div[contenteditable='true'][data-tab='10']")
                    )
                )
                caption_box.send_keys(sanitize_message(caption))

            # Click send button
            send_btn = self.driver.find_element(
                By.CSS_SELECTOR,
                "span[data-icon='send']"
            )
            send_btn.click()

            logger.info(f"File sent to {number}: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to send file to {number}: {e}")
            return False

    def read_unread_messages(self) -> List[Dict[str, Any]]:
        """
        Read unread messages from WhatsApp

        Returns:
            List of message dictionaries
        """
        if not self.is_logged_in:
            logger.error("Not logged in to WhatsApp")
            return []

        messages = []

        try:
            # Find all chats with unread messages
            unread_chats = self.driver.find_elements(
                By.CSS_SELECTOR,
                "div[data-testid='cell-frame-container']:has(span[data-testid='icon-unread-count'])"
            )

            for chat in unread_chats[:10]:  # Limit to 10 most recent
                try:
                    # Click chat
                    chat.click()
                    time.sleep(1)

                    # Get contact name/number
                    contact_elem = self.driver.find_element(
                        By.CSS_SELECTOR,
                        "span[data-testid='conversation-header-contact-name']"
                    )
                    contact = contact_elem.text

                    # Get unread messages
                    message_elems = self.driver.find_elements(
                        By.CSS_SELECTOR,
                        "div[data-testid='msg-container']:not(.message-in)"
                    )

                    for msg_elem in message_elems[-5:]:  # Last 5 messages
                        try:
                            text_elem = msg_elem.find_element(
                                By.CSS_SELECTOR,
                                "span.selectable-text"
                            )
                            text = text_elem.text

                            # Detect language
                            language = detect_language_from_message(text)

                            messages.append({
                                'from': contact,
                                'message': text,
                                'language': language,
                                'timestamp': time.time()
                            })
                        except NoSuchElementException:
                            continue

                except (NoSuchElementException, StaleElementReferenceException):
                    continue

            return messages

        except Exception as e:
            logger.error(f"Failed to read messages: {e}")
            return []

    def health_check(self) -> bool:
        """
        Check if WhatsApp connection is healthy

        Returns:
            True if healthy, False otherwise
        """
        if not self.driver:
            return False

        try:
            # Check if chat list is visible
            self.driver.find_element(
                By.CSS_SELECTOR,
                "div[data-testid='chat-list']"
            )

            self.last_health_check = time.time()
            return True

        except Exception:
            logger.warning("Health check failed - may need to reconnect")
            return False

    def reconnect(self) -> bool:
        """
        Attempt to reconnect to WhatsApp

        Returns:
            True if reconnected successfully
        """
        logger.info("Attempting to reconnect...")

        try:
            if self.driver:
                self.driver.refresh()
                time.sleep(3)

                if self.health_check():
                    logger.info("Reconnected successfully")
                    return True

            # If refresh doesn't work, try reinitializing
            self.close()
            return self.initialize()

        except Exception as e:
            logger.error(f"Reconnection failed: {e}")
            return False

    def close(self):
        """Close WhatsApp and browser"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WhatsApp closed")
            except Exception as e:
                logger.error(f"Error closing WhatsApp: {e}")

        self.driver = None
        self.is_logged_in = False

    def __del__(self):
        """Cleanup on deletion"""
        self.close()
