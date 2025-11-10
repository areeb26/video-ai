"""
Audio utilities for voice handler
"""
import os
import wave
import tempfile
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def check_microphone_access() -> bool:
    """
    Check if microphone is accessible

    Returns:
        True if microphone is accessible
    """
    try:
        import pyaudio

        p = pyaudio.PyAudio()

        # Try to open default input device
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=1024
        )

        stream.close()
        p.terminate()

        return True

    except Exception as e:
        logger.error(f"Microphone access check failed: {e}")
        return False


def get_audio_devices() -> list:
    """
    Get list of available audio devices

    Returns:
        List of audio device dictionaries
    """
    try:
        import pyaudio

        p = pyaudio.PyAudio()
        devices = []

        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            devices.append({
                'index': i,
                'name': info['name'],
                'channels': info['maxInputChannels'],
                'sample_rate': int(info['defaultSampleRate'])
            })

        p.terminate()
        return devices

    except Exception as e:
        logger.error(f"Failed to get audio devices: {e}")
        return []


def save_audio_to_file(audio_data: bytes, filename: str = None) -> Optional[str]:
    """
    Save audio data to WAV file

    Args:
        audio_data: Raw audio bytes
        filename: Output filename (optional)

    Returns:
        Path to saved file or None
    """
    try:
        if filename is None:
            temp_dir = tempfile.gettempdir()
            filename = os.path.join(temp_dir, f"audio_{os.getpid()}.wav")

        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(audio_data)

        return filename

    except Exception as e:
        logger.error(f"Failed to save audio: {e}")
        return None


def calculate_audio_volume(audio_data: bytes) -> float:
    """
    Calculate audio volume level

    Args:
        audio_data: Raw audio bytes

    Returns:
        Volume level (0.0 to 1.0)
    """
    try:
        import struct
        import math

        # Convert bytes to samples
        samples = struct.unpack(f'{len(audio_data)//2}h', audio_data)

        # Calculate RMS
        sum_squares = sum(sample**2 for sample in samples)
        rms = math.sqrt(sum_squares / len(samples))

        # Normalize to 0-1 range
        max_value = 32768  # Max value for 16-bit audio
        volume = min(rms / max_value, 1.0)

        return volume

    except Exception as e:
        logger.error(f"Failed to calculate volume: {e}")
        return 0.0


def detect_silence(audio_data: bytes, threshold: float = 0.01) -> bool:
    """
    Detect if audio is silence

    Args:
        audio_data: Raw audio bytes
        threshold: Silence threshold (0.0 to 1.0)

    Returns:
        True if audio is silence
    """
    volume = calculate_audio_volume(audio_data)
    return volume < threshold


def is_urdu_speech(text: str) -> bool:
    """
    Detect if text is in Urdu

    Args:
        text: Text to check

    Returns:
        True if text contains Urdu characters
    """
    import re
    urdu_chars = re.findall(r'[\u0600-\u06FF]', text)
    return len(urdu_chars) > len(text) * 0.3


def clean_speech_text(text: str) -> str:
    """
    Clean and normalize speech text

    Args:
        text: Raw speech text

    Returns:
        Cleaned text
    """
    # Remove extra whitespace
    text = ' '.join(text.split())

    # Remove common speech recognition artifacts
    text = text.replace('[', '').replace(']', '')
    text = text.replace('(', '').replace(')', '')

    return text.strip()


def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


class AudioBuffer:
    """Buffer for audio data"""

    def __init__(self, max_size: int = 10):
        """
        Initialize audio buffer

        Args:
            max_size: Maximum number of audio chunks to store
        """
        self.buffer = []
        self.max_size = max_size

    def add(self, audio_chunk: bytes):
        """Add audio chunk to buffer"""
        self.buffer.append(audio_chunk)

        # Keep only last max_size chunks
        if len(self.buffer) > self.max_size:
            self.buffer.pop(0)

    def get_all(self) -> bytes:
        """Get all audio data from buffer"""
        return b''.join(self.buffer)

    def clear(self):
        """Clear buffer"""
        self.buffer.clear()

    def is_empty(self) -> bool:
        """Check if buffer is empty"""
        return len(self.buffer) == 0

    def size(self) -> int:
        """Get number of chunks in buffer"""
        return len(self.buffer)
