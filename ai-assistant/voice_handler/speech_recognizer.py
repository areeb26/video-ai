"""
Speech Recognition Module
Converts speech to text using Google Speech Recognition API
"""
import speech_recognition as sr
import logging
from typing import Optional, Tuple
from .utils import clean_speech_text, is_urdu_speech

logger = logging.getLogger(__name__)


class SpeechRecognizer:
    """Speech-to-text converter supporting English and Urdu"""

    def __init__(
        self,
        language: str = "en",
        timeout: int = 5,
        phrase_time_limit: int = 10,
        energy_threshold: int = 4000
    ):
        """
        Initialize Speech Recognizer

        Args:
            language: Default language ('en' or 'ur')
            timeout: Listening timeout in seconds
            phrase_time_limit: Maximum phrase duration
            energy_threshold: Microphone energy threshold
        """
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.default_language = language
        self.timeout = timeout
        self.phrase_time_limit = phrase_time_limit

        # Configure recognizer
        self.recognizer.energy_threshold = energy_threshold
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8

        # Language codes for Google Speech API
        self.language_codes = {
            'en': 'en-US',
            'ur': 'ur-PK'
        }

        logger.info(f"Speech Recognizer initialized (language: {language})")

    def initialize_microphone(self, device_index: Optional[int] = None) -> bool:
        """
        Initialize microphone

        Args:
            device_index: Microphone device index (None for default)

        Returns:
            True if successful
        """
        try:
            self.microphone = sr.Microphone(device_index=device_index)

            # Adjust for ambient noise
            with self.microphone as source:
                logger.info("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)

            logger.info("Microphone initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize microphone: {e}")
            return False

    def listen(
        self,
        timeout: Optional[int] = None,
        phrase_time_limit: Optional[int] = None
    ) -> Optional[sr.AudioData]:
        """
        Listen for speech

        Args:
            timeout: Listening timeout (overrides default)
            phrase_time_limit: Phrase time limit (overrides default)

        Returns:
            AudioData object or None
        """
        if not self.microphone:
            if not self.initialize_microphone():
                return None

        timeout = timeout or self.timeout
        phrase_time_limit = phrase_time_limit or self.phrase_time_limit

        try:
            with self.microphone as source:
                logger.info("Listening...")
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )

            return audio

        except sr.WaitTimeoutError:
            logger.warning("Listening timeout")
            return None
        except Exception as e:
            logger.error(f"Error while listening: {e}")
            return None

    def recognize(
        self,
        audio: sr.AudioData,
        language: Optional[str] = None,
        show_all: bool = False
    ) -> Optional[str]:
        """
        Recognize speech from audio

        Args:
            audio: AudioData object
            language: Language code ('en' or 'ur', None for default)
            show_all: Return all alternatives

        Returns:
            Recognized text or None
        """
        language = language or self.default_language
        language_code = self.language_codes.get(language, 'en-US')

        try:
            # Use Google Speech Recognition
            text = self.recognizer.recognize_google(
                audio,
                language=language_code,
                show_all=show_all
            )

            if show_all:
                return text

            # Clean and return text
            cleaned_text = clean_speech_text(text)
            logger.info(f"Recognized: {cleaned_text}")

            return cleaned_text

        except sr.UnknownValueError:
            logger.warning("Could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Recognition service error: {e}")
            return None
        except Exception as e:
            logger.error(f"Recognition error: {e}")
            return None

    def listen_and_recognize(
        self,
        language: Optional[str] = None,
        timeout: Optional[int] = None,
        auto_detect_language: bool = False
    ) -> Tuple[Optional[str], str]:
        """
        Listen and recognize speech in one step

        Args:
            language: Language code
            timeout: Listening timeout
            auto_detect_language: Auto-detect language from speech

        Returns:
            Tuple of (text, detected_language)
        """
        # Listen for speech
        audio = self.listen(timeout=timeout)

        if not audio:
            return None, language or self.default_language

        # Recognize speech
        text = self.recognize(audio, language=language)

        if not text:
            return None, language or self.default_language

        # Auto-detect language if enabled
        detected_language = language or self.default_language

        if auto_detect_language and text:
            if is_urdu_speech(text):
                detected_language = 'ur'
            else:
                detected_language = 'en'

        return text, detected_language

    def recognize_from_file(
        self,
        audio_file: str,
        language: Optional[str] = None
    ) -> Optional[str]:
        """
        Recognize speech from audio file

        Args:
            audio_file: Path to audio file
            language: Language code

        Returns:
            Recognized text or None
        """
        try:
            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)

            return self.recognize(audio, language=language)

        except Exception as e:
            logger.error(f"Error recognizing from file: {e}")
            return None

    def test_microphone(self) -> bool:
        """
        Test microphone and recognition

        Returns:
            True if microphone is working
        """
        try:
            logger.info("Testing microphone... Please say something.")

            audio = self.listen(timeout=5)

            if not audio:
                logger.error("No audio captured")
                return False

            text = self.recognize(audio)

            if text:
                logger.info(f"Test successful! Heard: {text}")
                return True
            else:
                logger.warning("Could not recognize speech")
                return False

        except Exception as e:
            logger.error(f"Microphone test failed: {e}")
            return False

    def set_energy_threshold(self, threshold: int):
        """
        Set microphone energy threshold

        Args:
            threshold: Energy threshold value
        """
        self.recognizer.energy_threshold = threshold
        logger.info(f"Energy threshold set to {threshold}")

    def calibrate(self, duration: int = 2):
        """
        Calibrate for ambient noise

        Args:
            duration: Calibration duration in seconds
        """
        if not self.microphone:
            if not self.initialize_microphone():
                return

        try:
            with self.microphone as source:
                logger.info(f"Calibrating for {duration} seconds...")
                self.recognizer.adjust_for_ambient_noise(source, duration=duration)

            logger.info(f"Calibration complete. Energy threshold: {self.recognizer.energy_threshold}")

        except Exception as e:
            logger.error(f"Calibration failed: {e}")

    def get_recognizer_info(self) -> dict:
        """
        Get recognizer configuration info

        Returns:
            Dictionary with recognizer info
        """
        return {
            'energy_threshold': self.recognizer.energy_threshold,
            'dynamic_energy_threshold': self.recognizer.dynamic_energy_threshold,
            'pause_threshold': self.recognizer.pause_threshold,
            'timeout': self.timeout,
            'phrase_time_limit': self.phrase_time_limit,
            'default_language': self.default_language,
            'supported_languages': list(self.language_codes.keys())
        }
