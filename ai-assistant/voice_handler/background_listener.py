"""
Background Listener
Continuously listens for wake words and processes voice commands
"""
import threading
import time
import logging
from typing import Optional, Callable
from .speech_recognizer import SpeechRecognizer
from .text_to_speech import TextToSpeech
from .wake_word_detector import WakeWordDetector, WakeWordValidator

logger = logging.getLogger(__name__)


class BackgroundListener:
    """Background voice command listener"""

    def __init__(
        self,
        command_callback: Callable[[str, str], str],
        language: str = "en",
        wake_word_required: bool = True
    ):
        """
        Initialize Background Listener

        Args:
            command_callback: Callback function(command, language) -> response
            language: Default language
            wake_word_required: Require wake word before commands
        """
        self.command_callback = command_callback
        self.default_language = language
        self.wake_word_required = wake_word_required

        # Initialize components
        self.speech_recognizer = SpeechRecognizer(language=language)
        self.tts = TextToSpeech(language=language)
        self.wake_word_detector = WakeWordDetector()
        self.validator = WakeWordValidator()

        # State
        self.is_running = False
        self.is_listening = False
        self.listener_thread: Optional[threading.Thread] = None
        self.command_count = 0
        self.error_count = 0

        # Configuration
        self.continuous_mode = False
        self.timeout = 5
        self.response_enabled = True

        logger.info("Background Listener initialized")

    def start(self, continuous: bool = True):
        """
        Start background listening

        Args:
            continuous: Continue listening after processing command
        """
        if self.is_running:
            logger.warning("Listener already running")
            return

        self.continuous_mode = continuous
        self.is_running = True

        # Start listener thread
        self.listener_thread = threading.Thread(
            target=self._listen_loop,
            daemon=True
        )
        self.listener_thread.start()

        logger.info("Background listener started")

        # Announce activation
        if self.response_enabled:
            self.tts.speak_async(
                "Voice assistant activated" if self.default_language == 'en'
                else "وائس اسسٹنٹ فعال ہو گیا",
                language=self.default_language
            )

    def stop(self):
        """Stop background listening"""
        if not self.is_running:
            return

        self.is_running = False

        if self.listener_thread:
            self.listener_thread.join(timeout=2)

        logger.info("Background listener stopped")

        # Announce deactivation
        if self.response_enabled:
            self.tts.speak_async(
                "Voice assistant deactivated" if self.default_language == 'en'
                else "وائس اسسٹنٹ غیر فعال ہو گیا",
                language=self.default_language
            )

    def _listen_loop(self):
        """Main listening loop"""
        logger.info("Starting listen loop...")

        # Initialize microphone
        if not self.speech_recognizer.initialize_microphone():
            logger.error("Failed to initialize microphone")
            self.is_running = False
            return

        while self.is_running:
            try:
                self._listen_cycle()

                # Small delay to prevent CPU overuse
                time.sleep(0.1)

            except KeyboardInterrupt:
                logger.info("Listener interrupted by user")
                break
            except Exception as e:
                logger.error(f"Error in listen loop: {e}")
                self.error_count += 1

                # Stop if too many errors
                if self.error_count > 10:
                    logger.error("Too many errors, stopping listener")
                    self.is_running = False
                    break

                time.sleep(1)

        logger.info("Listen loop ended")

    def _listen_cycle(self):
        """Single listen cycle"""
        # Listen for speech
        self.is_listening = True
        text, language = self.speech_recognizer.listen_and_recognize(
            timeout=self.timeout,
            auto_detect_language=True
        )
        self.is_listening = False

        if not text:
            return

        logger.info(f"Heard: {text}")

        # Check for wake word if required
        if self.wake_word_required:
            detected, wake_word = self.wake_word_detector.detect(text)

            if not detected:
                return

            # Extract command after wake word
            command = self.wake_word_detector.extract_command(text, wake_word)

        else:
            command = text

        # Validate command
        if not self.validator.is_valid_command(command, language):
            logger.warning(f"Invalid command: {command}")

            if self.response_enabled:
                self.tts.speak_async(
                    "I didn't understand that command" if language == 'en'
                    else "میں نے یہ کمانڈ نہیں سمجھی",
                    language=language
                )
            return

        # Process command
        self._process_command(command, language)

    def _process_command(self, command: str, language: str):
        """
        Process voice command

        Args:
            command: Command text
            language: Language code
        """
        try:
            logger.info(f"Processing command: {command} ({language})")

            # Acknowledge
            if self.response_enabled:
                self.tts.speak_async(
                    "Processing..." if language == 'en' else "پروسیس کر رہا ہوں...",
                    language=language
                )

            # Execute command callback
            response = self.command_callback(command, language)

            self.command_count += 1

            # Speak response
            if response and self.response_enabled:
                self.tts.speak_async(response, language=language)

            logger.info(f"Command processed successfully")

        except Exception as e:
            logger.error(f"Error processing command: {e}")

            if self.response_enabled:
                self.tts.speak_async(
                    f"Error: {str(e)}" if language == 'en'
                    else f"خرابی: {str(e)}",
                    language=language
                )

    def toggle_response(self):
        """Toggle voice responses on/off"""
        self.response_enabled = not self.response_enabled
        logger.info(f"Voice responses: {'enabled' if self.response_enabled else 'disabled'}")

    def set_language(self, language: str):
        """
        Change default language

        Args:
            language: Language code ('en' or 'ur')
        """
        self.default_language = language
        self.speech_recognizer.default_language = language
        self.tts.default_language = language
        logger.info(f"Language changed to: {language}")

    def add_wake_word(self, wake_word: str):
        """
        Add custom wake word

        Args:
            wake_word: Wake word to add
        """
        self.wake_word_detector.add_wake_word(wake_word)

    def remove_wake_word(self, wake_word: str):
        """
        Remove wake word

        Args:
            wake_word: Wake word to remove
        """
        self.wake_word_detector.remove_wake_word(wake_word)

    def calibrate_microphone(self, duration: int = 2):
        """
        Calibrate microphone for ambient noise

        Args:
            duration: Calibration duration in seconds
        """
        logger.info("Calibrating microphone...")
        self.speech_recognizer.calibrate(duration=duration)

    def get_status(self) -> dict:
        """
        Get listener status

        Returns:
            Status dictionary
        """
        return {
            'is_running': self.is_running,
            'is_listening': self.is_listening,
            'continuous_mode': self.continuous_mode,
            'wake_word_required': self.wake_word_required,
            'response_enabled': self.response_enabled,
            'command_count': self.command_count,
            'error_count': self.error_count,
            'default_language': self.default_language,
            'wake_word_stats': self.wake_word_detector.get_stats(),
            'recognizer_info': self.speech_recognizer.get_recognizer_info(),
            'tts_info': self.tts.get_engine_info()
        }

    def reset_stats(self):
        """Reset statistics"""
        self.command_count = 0
        self.error_count = 0
        self.wake_word_detector.reset_stats()
        logger.info("Stats reset")

    def __del__(self):
        """Cleanup"""
        self.stop()


class VoiceCommandHandler:
    """Handler for processing voice commands with assistant integration"""

    def __init__(self, assistant_url: str = "http://localhost:8001"):
        """
        Initialize Voice Command Handler

        Args:
            assistant_url: URL of the AI assistant API
        """
        self.assistant_url = assistant_url

    def process_command(self, command: str, language: str) -> str:
        """
        Process voice command through assistant

        Args:
            command: Command text
            language: Language code

        Returns:
            Response text
        """
        try:
            import requests

            # Send to assistant API
            response = requests.post(
                f"{self.assistant_url}/api/v1/assistant",
                json={
                    "message": command,
                    "language": language
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('message', 'Command processed')
            else:
                return "Error processing command"

        except requests.exceptions.Timeout:
            return "Request timed out"
        except requests.exceptions.ConnectionError:
            return "Could not connect to assistant"
        except Exception as e:
            logger.error(f"Error in command handler: {e}")
            return f"Error: {str(e)}"
