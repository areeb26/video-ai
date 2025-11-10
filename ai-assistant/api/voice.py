"""
Voice API endpoints
Provides voice recognition and text-to-speech capabilities
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Optional
import logging
import os
import tempfile

from ..schemas.voice import (
    VoiceCommandRequest,
    VoiceCommandResponse,
    VoiceSpeakRequest,
    VoiceSpeakResponse,
    VoiceListenerConfigRequest,
    VoiceListenerStatusResponse,
    VoiceWakeWordRequest,
    VoiceCalibrationRequest,
    VoiceDevicesResponse,
    VoiceTestResponse
)
from ..voice_handler import (
    SpeechRecognizer,
    TextToSpeech,
    WakeWordDetector,
    BackgroundListener
)
from ..voice_handler.background_listener import VoiceCommandHandler
from ..voice_handler.utils import get_audio_devices, check_microphone_access

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/voice", tags=["voice"])

# Global instances
speech_recognizer: Optional[SpeechRecognizer] = None
tts: Optional[TextToSpeech] = None
wake_word_detector: Optional[WakeWordDetector] = None
background_listener: Optional[BackgroundListener] = None
voice_command_handler: Optional[VoiceCommandHandler] = None


@router.on_event("startup")
async def startup_voice():
    """Initialize voice handlers on startup"""
    global speech_recognizer, tts, wake_word_detector, voice_command_handler

    try:
        # Initialize components
        speech_recognizer = SpeechRecognizer()
        tts = TextToSpeech()
        wake_word_detector = WakeWordDetector()
        voice_command_handler = VoiceCommandHandler()

        logger.info("Voice handlers initialized")

    except Exception as e:
        logger.error(f"Failed to initialize voice handlers: {e}")


@router.post("/recognize", response_model=VoiceCommandResponse)
async def recognize_speech(
    audio: UploadFile = File(None),
    text: Optional[str] = None,
    language: str = "en"
):
    """
    Recognize speech from audio file or microphone

    Args:
        audio: Audio file (optional)
        text: Or provide text directly
        language: Language code

    Returns:
        Recognition result with assistant response
    """
    try:
        if not speech_recognizer:
            raise HTTPException(status_code=500, detail="Speech recognizer not initialized")

        recognized_text = None

        # If audio file provided
        if audio:
            # Save uploaded file temporarily
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            temp_file.write(await audio.read())
            temp_file.close()

            # Recognize speech
            recognized_text = speech_recognizer.recognize_from_file(temp_file.name, language=language)

            # Clean up
            os.unlink(temp_file.name)

        # If text provided directly
        elif text:
            recognized_text = text

        # Listen from microphone
        else:
            recognized_text, detected_language = speech_recognizer.listen_and_recognize(
                language=language,
                auto_detect_language=True
            )
            language = detected_language

        if not recognized_text:
            raise HTTPException(status_code=400, detail="Could not recognize speech")

        # Process command through assistant
        response = voice_command_handler.process_command(recognized_text, language)

        return VoiceCommandResponse(
            success=True,
            text=recognized_text,
            response=response,
            language=language
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recognizing speech: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/speak", response_model=VoiceSpeakResponse)
async def speak_text(request: VoiceSpeakRequest):
    """
    Convert text to speech

    Args:
        request: Speech request with text and settings

    Returns:
        Speech result
    """
    try:
        if not tts:
            raise HTTPException(status_code=500, detail="TTS not initialized")

        if request.save_to_file:
            # Save to file
            filename = request.filename or tempfile.mktemp(suffix=".mp3")
            success = tts.save_to_file(request.text, filename, language=request.language)

            if success:
                return VoiceSpeakResponse(
                    success=True,
                    audio_file=filename
                )
            else:
                raise HTTPException(status_code=500, detail="Failed to save audio")

        else:
            # Speak directly
            success = tts.speak(request.text, language=request.language, wait=False)

            return VoiceSpeakResponse(
                success=success,
                error=None if success else "Failed to speak"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error speaking text: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/listener/start")
async def start_listener(continuous: bool = True):
    """
    Start background voice listener

    Args:
        continuous: Continue listening after commands

    Returns:
        Status message
    """
    global background_listener

    try:
        if background_listener and background_listener.is_running:
            return {"message": "Listener already running"}

        # Create new listener if needed
        if not background_listener:
            background_listener = BackgroundListener(
                command_callback=voice_command_handler.process_command
            )

        background_listener.start(continuous=continuous)

        return {
            "message": "Voice listener started",
            "continuous": continuous
        }

    except Exception as e:
        logger.error(f"Error starting listener: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/listener/stop")
async def stop_listener():
    """Stop background voice listener"""
    try:
        if not background_listener or not background_listener.is_running:
            return {"message": "Listener not running"}

        background_listener.stop()

        return {"message": "Voice listener stopped"}

    except Exception as e:
        logger.error(f"Error stopping listener: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/listener/status", response_model=VoiceListenerStatusResponse)
async def get_listener_status():
    """Get voice listener status"""
    try:
        if not background_listener:
            return VoiceListenerStatusResponse(
                is_running=False,
                is_listening=False,
                continuous_mode=False,
                wake_word_required=True,
                response_enabled=True,
                command_count=0,
                error_count=0,
                default_language="en",
                wake_word_stats={}
            )

        status = background_listener.get_status()

        return VoiceListenerStatusResponse(**status)

    except Exception as e:
        logger.error(f"Error getting listener status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/listener/configure")
async def configure_listener(config: VoiceListenerConfigRequest):
    """
    Configure voice listener settings

    Args:
        config: Configuration settings

    Returns:
        Updated configuration
    """
    try:
        if not background_listener:
            raise HTTPException(status_code=400, detail="Listener not initialized")

        # Update settings
        if config.wake_word_required is not None:
            background_listener.wake_word_required = config.wake_word_required

        if config.continuous_mode is not None:
            background_listener.continuous_mode = config.continuous_mode

        if config.response_enabled is not None:
            background_listener.response_enabled = config.response_enabled

        if config.language:
            background_listener.set_language(config.language)

        if config.speech_rate and tts:
            tts.set_rate(config.speech_rate)

        if config.volume and tts:
            tts.set_volume(config.volume)

        return {
            "message": "Configuration updated",
            "settings": background_listener.get_status()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error configuring listener: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/wake-word/add")
async def add_wake_word(request: VoiceWakeWordRequest):
    """Add custom wake word"""
    try:
        if not wake_word_detector:
            raise HTTPException(status_code=500, detail="Wake word detector not initialized")

        wake_word_detector.add_wake_word(request.wake_word, language=request.language)

        if background_listener:
            background_listener.add_wake_word(request.wake_word)

        return {
            "message": f"Wake word '{request.wake_word}' added",
            "wake_words": wake_word_detector.get_wake_words()
        }

    except Exception as e:
        logger.error(f"Error adding wake word: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/wake-word/{wake_word}")
async def remove_wake_word(wake_word: str):
    """Remove wake word"""
    try:
        if not wake_word_detector:
            raise HTTPException(status_code=500, detail="Wake word detector not initialized")

        success = wake_word_detector.remove_wake_word(wake_word)

        if success and background_listener:
            background_listener.remove_wake_word(wake_word)

        return {
            "message": f"Wake word '{wake_word}' removed" if success else "Wake word not found",
            "wake_words": wake_word_detector.get_wake_words()
        }

    except Exception as e:
        logger.error(f"Error removing wake word: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/wake-words")
async def list_wake_words():
    """List all wake words"""
    try:
        if not wake_word_detector:
            raise HTTPException(status_code=500, detail="Wake word detector not initialized")

        return {
            "wake_words": wake_word_detector.get_wake_words(),
            "stats": wake_word_detector.get_stats()
        }

    except Exception as e:
        logger.error(f"Error listing wake words: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calibrate")
async def calibrate_microphone(config: VoiceCalibrationRequest):
    """Calibrate microphone for ambient noise"""
    try:
        if not speech_recognizer:
            raise HTTPException(status_code=500, detail="Speech recognizer not initialized")

        speech_recognizer.calibrate(duration=config.duration)

        if background_listener:
            background_listener.calibrate_microphone(duration=config.duration)

        return {
            "message": "Microphone calibrated",
            "duration": config.duration,
            "energy_threshold": speech_recognizer.recognizer.energy_threshold
        }

    except Exception as e:
        logger.error(f"Error calibrating microphone: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/devices", response_model=VoiceDevicesResponse)
async def list_audio_devices():
    """List available audio input devices"""
    try:
        devices = get_audio_devices()

        return VoiceDevicesResponse(
            devices=devices,
            default_device=0 if devices else None
        )

    except Exception as e:
        logger.error(f"Error listing devices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test/microphone", response_model=VoiceTestResponse)
async def test_microphone():
    """Test microphone and speech recognition"""
    try:
        # Check microphone access
        if not check_microphone_access():
            return VoiceTestResponse(
                success=False,
                message="Microphone not accessible"
            )

        if not speech_recognizer:
            raise HTTPException(status_code=500, detail="Speech recognizer not initialized")

        # Test microphone
        success = speech_recognizer.test_microphone()

        return VoiceTestResponse(
            success=success,
            message="Microphone test successful" if success else "Microphone test failed"
        )

    except Exception as e:
        logger.error(f"Error testing microphone: {e}")
        return VoiceTestResponse(
            success=False,
            message=str(e)
        )


@router.get("/test/tts", response_model=VoiceTestResponse)
async def test_tts(language: str = "en"):
    """Test text-to-speech"""
    try:
        if not tts:
            raise HTTPException(status_code=500, detail="TTS not initialized")

        success = tts.test(language=language)

        return VoiceTestResponse(
            success=success,
            message="TTS test successful" if success else "TTS test failed"
        )

    except Exception as e:
        logger.error(f"Error testing TTS: {e}")
        return VoiceTestResponse(
            success=False,
            message=str(e)
        )


@router.get("/info")
async def get_voice_info():
    """Get voice system information"""
    try:
        info = {
            "speech_recognizer": speech_recognizer.get_recognizer_info() if speech_recognizer else None,
            "tts": tts.get_engine_info() if tts else None,
            "wake_words": wake_word_detector.get_wake_words() if wake_word_detector else None,
            "listener": background_listener.get_status() if background_listener else None
        }

        return info

    except Exception as e:
        logger.error(f"Error getting voice info: {e}")
        raise HTTPException(status_code=500, detail=str(e))
