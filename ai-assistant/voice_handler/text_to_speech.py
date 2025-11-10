"""
Text-to-Speech Module
Converts text to speech using pyttsx3
"""
import pyttsx3
import logging
from typing import Optional, List
import threading
import queue

logger = logging.getLogger(__name__)


class TextToSpeech:
    """Text-to-speech converter supporting multiple languages"""

    def __init__(
        self,
        language: str = "en",
        rate: int = 150,
        volume: float = 0.9
    ):
        """
        Initialize Text-to-Speech

        Args:
            language: Default language ('en' or 'ur')
            rate: Speech rate (words per minute)
            volume: Volume level (0.0 to 1.0)
        """
        self.engine = None
        self.default_language = language
        self.rate = rate
        self.volume = volume
        self.is_speaking = False
        self.speech_queue = queue.Queue()

        # Initialize engine
        self._initialize_engine()

        logger.info(f"Text-to-Speech initialized (language: {language})")

    def _initialize_engine(self):
        """Initialize TTS engine"""
        try:
            self.engine = pyttsx3.init()

            # Set properties
            self.engine.setProperty('rate', self.rate)
            self.engine.setProperty('volume', self.volume)

            # Try to set voice
            self._set_voice(self.default_language)

            logger.info("TTS engine initialized")

        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}")
            self.engine = None

    def _set_voice(self, language: str):
        """
        Set voice for language

        Args:
            language: Language code
        """
        if not self.engine:
            return

        try:
            voices = self.engine.getProperty('voices')

            # Try to find voice for language
            voice_keywords = {
                'en': ['english', 'en_', 'en-'],
                'ur': ['urdu', 'ur_', 'ur-', 'hindi', 'hi_']  # Urdu often shares with Hindi voices
            }

            keywords = voice_keywords.get(language, voice_keywords['en'])

            for voice in voices:
                voice_id_lower = voice.id.lower()
                voice_name_lower = voice.name.lower()

                for keyword in keywords:
                    if keyword in voice_id_lower or keyword in voice_name_lower:
                        self.engine.setProperty('voice', voice.id)
                        logger.info(f"Voice set to: {voice.name}")
                        return

            # If no specific voice found, use first available
            if voices:
                self.engine.setProperty('voice', voices[0].id)
                logger.warning(f"Using default voice: {voices[0].name}")

        except Exception as e:
            logger.error(f"Error setting voice: {e}")

    def speak(
        self,
        text: str,
        language: Optional[str] = None,
        wait: bool = True
    ) -> bool:
        """
        Speak text

        Args:
            text: Text to speak
            language: Language code (None for default)
            wait: Wait for speech to complete

        Returns:
            True if successful
        """
        if not self.engine:
            logger.error("TTS engine not initialized")
            return False

        if not text:
            return False

        try:
            # Set voice for language if specified
            if language and language != self.default_language:
                self._set_voice(language)

            self.is_speaking = True

            # Speak
            self.engine.say(text)

            if wait:
                self.engine.runAndWait()
            else:
                # Run in separate thread
                threading.Thread(
                    target=self._speak_thread,
                    args=(text,),
                    daemon=True
                ).start()

            self.is_speaking = False
            logger.info(f"Spoke: {text[:50]}...")

            return True

        except Exception as e:
            logger.error(f"Error speaking: {e}")
            self.is_speaking = False
            return False

    def _speak_thread(self, text: str):
        """Speak in separate thread"""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logger.error(f"Error in speak thread: {e}")

    def speak_async(self, text: str, language: Optional[str] = None):
        """
        Speak asynchronously (non-blocking)

        Args:
            text: Text to speak
            language: Language code
        """
        self.speech_queue.put((text, language))

        # Start queue processor if not running
        if not hasattr(self, '_queue_thread') or not self._queue_thread.is_alive():
            self._queue_thread = threading.Thread(
                target=self._process_speech_queue,
                daemon=True
            )
            self._queue_thread.start()

    def _process_speech_queue(self):
        """Process speech queue"""
        while True:
            try:
                text, language = self.speech_queue.get(timeout=1)
                self.speak(text, language=language, wait=True)
                self.speech_queue.task_done()
            except queue.Empty:
                break
            except Exception as e:
                logger.error(f"Error processing speech queue: {e}")

    def stop(self):
        """Stop current speech"""
        if self.engine:
            try:
                self.engine.stop()
                self.is_speaking = False
            except Exception as e:
                logger.error(f"Error stopping speech: {e}")

    def set_rate(self, rate: int):
        """
        Set speech rate

        Args:
            rate: Words per minute
        """
        if self.engine:
            self.rate = rate
            self.engine.setProperty('rate', rate)
            logger.info(f"Speech rate set to {rate}")

    def set_volume(self, volume: float):
        """
        Set volume

        Args:
            volume: Volume level (0.0 to 1.0)
        """
        if self.engine:
            self.volume = max(0.0, min(1.0, volume))
            self.engine.setProperty('volume', self.volume)
            logger.info(f"Volume set to {self.volume}")

    def get_available_voices(self) -> List[dict]:
        """
        Get list of available voices

        Returns:
            List of voice dictionaries
        """
        if not self.engine:
            return []

        try:
            voices = self.engine.getProperty('voices')
            return [
                {
                    'id': voice.id,
                    'name': voice.name,
                    'languages': voice.languages,
                    'gender': voice.gender
                }
                for voice in voices
            ]
        except Exception as e:
            logger.error(f"Error getting voices: {e}")
            return []

    def save_to_file(self, text: str, filename: str, language: Optional[str] = None) -> bool:
        """
        Save speech to audio file

        Args:
            text: Text to convert
            filename: Output filename
            language: Language code

        Returns:
            True if successful
        """
        if not self.engine:
            return False

        try:
            # Set voice for language if specified
            if language and language != self.default_language:
                self._set_voice(language)

            self.engine.save_to_file(text, filename)
            self.engine.runAndWait()

            logger.info(f"Speech saved to {filename}")
            return True

        except Exception as e:
            logger.error(f"Error saving speech to file: {e}")
            return False

    def test(self, text: Optional[str] = None, language: Optional[str] = None) -> bool:
        """
        Test TTS

        Args:
            text: Test text (default provided)
            language: Language code

        Returns:
            True if successful
        """
        if not text:
            if language == 'ur':
                text = "یہ ایک ٹیسٹ ہے"  # This is a test
            else:
                text = "This is a test"

        return self.speak(text, language=language)

    def get_engine_info(self) -> dict:
        """
        Get TTS engine info

        Returns:
            Dictionary with engine info
        """
        info = {
            'rate': self.rate,
            'volume': self.volume,
            'default_language': self.default_language,
            'is_speaking': self.is_speaking,
            'queue_size': self.speech_queue.qsize()
        }

        if self.engine:
            try:
                voices = self.engine.getProperty('voices')
                info['available_voices'] = len(voices)
                info['current_voice'] = self.engine.getProperty('voice')
            except:
                pass

        return info

    def __del__(self):
        """Cleanup"""
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass
