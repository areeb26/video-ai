"""
Mood Detection Module
Detects mood from voice tone and text analysis
"""
from typing import Dict, Any, Optional, Tuple
import re
import struct
import math


class MoodDetector:
    """Detects user mood from voice and text"""

    def __init__(self):
        # Mood keywords for text analysis
        self.mood_keywords = {
            'happy': [
                'happy', 'great', 'awesome', 'wonderful', 'excellent', 'fantastic',
                'good', 'nice', 'pleased', 'delighted', 'excited', 'love', 'enjoy',
                'amazing', 'perfect', 'brilliant', 'yay', 'hooray', '😊', '😃', '😄'
            ],
            'sad': [
                'sad', 'unhappy', 'depressed', 'down', 'disappointed', 'upset',
                'miserable', 'terrible', 'awful', 'bad', 'horrible', 'poor',
                'unfortunate', 'regret', '😢', '😞', '😔'
            ],
            'angry': [
                'angry', 'mad', 'furious', 'annoyed', 'frustrated', 'irritated',
                'outraged', 'hate', 'disgusted', 'infuriated', 'enraged', '😠', '😡', '🤬'
            ],
            'anxious': [
                'worried', 'anxious', 'nervous', 'stressed', 'concerned', 'afraid',
                'scared', 'fearful', 'uneasy', 'tense', 'panic', '😰', '😨'
            ],
            'excited': [
                'excited', 'thrilled', 'pumped', 'eager', 'enthusiastic', 'energetic',
                'motivated', 'inspired', 'can\'t wait', '🎉', '🎊', '😆'
            ],
            'neutral': [
                'okay', 'fine', 'alright', 'normal', 'regular', 'usual'
            ]
        }

        # Urdu mood keywords
        self.urdu_mood_keywords = {
            'happy': ['خوش', 'بہترین', 'شاندار', 'اچھا', 'مزہ'],
            'sad': ['اداس', 'غمگین', 'مایوس', 'برا', 'افسوس'],
            'angry': ['غصہ', 'ناراض', 'غضبناک', 'نفرت'],
            'anxious': ['پریشان', 'فکر مند', 'خوفزدہ', 'گھبرایا ہوا'],
            'excited': ['پرجوش', 'متجسس', 'بے چین', 'بےتاب']
        }

    def detect_mood_from_text(self, text: str, language: str = "en") -> Dict[str, Any]:
        """Detect mood from text content"""
        text_lower = text.lower()

        # Choose keyword set based on language
        keywords = self.mood_keywords if language == 'en' else self.urdu_mood_keywords

        # Score each mood
        mood_scores = {}
        for mood, mood_words in keywords.items():
            score = sum(1 for word in mood_words if word in text_lower or word in text)
            mood_scores[mood] = score

        # Analyze punctuation and capitalization for intensity
        exclamation_count = text.count('!')
        question_count = text.count('?')
        caps_ratio = sum(1 for c in text if c.isupper()) / len(text) if text else 0

        # Adjust scores based on intensity markers
        if exclamation_count > 1 or caps_ratio > 0.3:
            # High intensity - boost excited, angry, or happy
            if mood_scores.get('excited', 0) > 0:
                mood_scores['excited'] *= 1.5
            if mood_scores.get('angry', 0) > 0:
                mood_scores['angry'] *= 1.5
            if mood_scores.get('happy', 0) > 0:
                mood_scores['happy'] *= 1.2

        # Get dominant mood
        if all(score == 0 for score in mood_scores.values()):
            detected_mood = 'neutral'
            confidence = 0.5
        else:
            detected_mood = max(mood_scores.items(), key=lambda x: x[1])[0]
            total_score = sum(mood_scores.values())
            confidence = mood_scores[detected_mood] / total_score if total_score > 0 else 0.5

        # Normalize confidence to 0-1 range
        confidence = min(confidence, 1.0)

        return {
            'mood': detected_mood,
            'confidence': confidence,
            'mood_breakdown': mood_scores,
            'intensity_markers': {
                'exclamations': exclamation_count,
                'questions': question_count,
                'caps_ratio': caps_ratio
            }
        }

    def detect_mood_from_voice(
        self,
        pitch: Optional[float] = None,
        energy: Optional[float] = None,
        rate: Optional[float] = None,
        audio_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """Detect mood from voice characteristics"""

        mood_scores = {
            'happy': 0.0,
            'sad': 0.0,
            'angry': 0.0,
            'anxious': 0.0,
            'excited': 0.0,
            'neutral': 0.5
        }

        if audio_file:
            # Extract features from audio file
            pitch, energy, rate = self._extract_audio_features(audio_file)

        if pitch is not None:
            # High pitch often indicates happiness or excitement
            if pitch > 200:  # Hz
                mood_scores['happy'] += 0.3
                mood_scores['excited'] += 0.4
            # Low pitch might indicate sadness
            elif pitch < 120:
                mood_scores['sad'] += 0.4

        if energy is not None:
            # High energy indicates excitement or anger
            if energy > 0.7:
                mood_scores['excited'] += 0.3
                mood_scores['angry'] += 0.2
            # Low energy indicates sadness or neutral
            elif energy < 0.3:
                mood_scores['sad'] += 0.3
                mood_scores['neutral'] += 0.2

        if rate is not None:
            # Fast speaking rate indicates excitement or anxiety
            if rate > 150:  # words per minute
                mood_scores['excited'] += 0.3
                mood_scores['anxious'] += 0.2
            # Slow speaking rate indicates sadness or calm
            elif rate < 100:
                mood_scores['sad'] += 0.3
                mood_scores['neutral'] += 0.2

        # Get dominant mood
        detected_mood = max(mood_scores.items(), key=lambda x: x[1])[0]
        confidence = mood_scores[detected_mood]

        return {
            'mood': detected_mood,
            'confidence': min(confidence, 1.0),
            'mood_breakdown': mood_scores,
            'voice_features': {
                'pitch': pitch,
                'energy': energy,
                'rate': rate
            }
        }

    def detect_mood_combined(
        self,
        text: Optional[str] = None,
        language: str = "en",
        pitch: Optional[float] = None,
        energy: Optional[float] = None,
        rate: Optional[float] = None,
        audio_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """Detect mood using both text and voice"""

        text_mood = None
        voice_mood = None

        # Analyze text if provided
        if text:
            text_mood = self.detect_mood_from_text(text, language)

        # Analyze voice if features provided
        if pitch or energy or rate or audio_file:
            voice_mood = self.detect_mood_from_voice(pitch, energy, rate, audio_file)

        # Combine results
        if text_mood and voice_mood:
            # Average the mood scores
            combined_scores = {}
            all_moods = set(text_mood['mood_breakdown'].keys()) | set(voice_mood['mood_breakdown'].keys())

            for mood in all_moods:
                text_score = text_mood['mood_breakdown'].get(mood, 0) * text_mood['confidence']
                voice_score = voice_mood['mood_breakdown'].get(mood, 0) * voice_mood['confidence']
                combined_scores[mood] = (text_score + voice_score) / 2

            detected_mood = max(combined_scores.items(), key=lambda x: x[1])[0]
            confidence = combined_scores[detected_mood]

            return {
                'mood': detected_mood,
                'confidence': min(confidence, 1.0),
                'mood_breakdown': combined_scores,
                'text_mood': text_mood['mood'],
                'voice_mood': voice_mood['mood'],
                'sources': ['text', 'voice']
            }

        elif text_mood:
            return {**text_mood, 'sources': ['text']}

        elif voice_mood:
            return {**voice_mood, 'sources': ['voice']}

        else:
            return {
                'mood': 'neutral',
                'confidence': 0.5,
                'mood_breakdown': {'neutral': 0.5},
                'sources': []
            }

    def _extract_audio_features(self, audio_file: str) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """Extract pitch, energy, and rate from audio file"""
        # This is a placeholder - in production, you'd use a library like librosa or parselmouth
        # For now, return None values
        try:
            # Placeholder for audio analysis
            # In production, use:
            # import librosa
            # y, sr = librosa.load(audio_file)
            # pitch = librosa.pitch_tuning(y)
            # energy = librosa.feature.rms(y=y).mean()
            # rate = self._estimate_speaking_rate(y, sr)
            return None, None, None
        except Exception:
            return None, None, None

    def get_mood_recommendation(self, mood: str, confidence: float) -> str:
        """Get recommendation based on detected mood"""
        recommendations = {
            'happy': "Great! Let's keep that positive energy going. What would you like to accomplish today?",
            'sad': "I'm here to help. Sometimes breaking tasks into smaller steps can make things feel more manageable.",
            'angry': "I understand you're frustrated. Let's focus on what we can control and make progress on your tasks.",
            'anxious': "Take a deep breath. Let's prioritize your tasks and tackle them one at a time.",
            'excited': "That's wonderful energy! Let's channel that into getting things done.",
            'neutral': "Ready to work? Let me know what you'd like to accomplish."
        }

        urdu_recommendations = {
            'happy': "بہترین! آئیے اس مثبت توانائی کو جاری رکھیں۔ آج آپ کیا کرنا چاہیں گے؟",
            'sad': "میں یہاں مدد کے لیے ہوں۔ کبھی کبھی کاموں کو چھوٹے مراحل میں تقسیم کرنے سے چیزیں زیادہ قابل انتظام محسوس ہوتی ہیں۔",
            'angry': "میں سمجھتا ہوں کہ آپ مایوس ہیں۔ آئیے ان چیزوں پر توجہ مرکوز کریں جن پر ہم قابو پا سکتے ہیں۔",
            'anxious': "ایک گہرا سانس لیں۔ آئیے اپنے کاموں کو ترجیح دیں اور ایک وقت میں ایک سے نمٹیں۔",
            'excited': "یہ شاندار توانائی ہے! آئیے اسے کام مکمل کرنے میں لگائیں۔",
            'neutral': "کام کے لیے تیار ہیں؟ مجھے بتائیں کہ آپ کیا کرنا چاہتے ہیں۔"
        }

        return recommendations.get(mood, recommendations['neutral'])

    def get_mood_urdu_recommendation(self, mood: str, confidence: float) -> str:
        """Get Urdu recommendation based on detected mood"""
        urdu_recommendations = {
            'happy': "بہترین! آئیے اس مثبت توانائی کو جاری رکھیں۔ آج آپ کیا کرنا چاہیں گے؟",
            'sad': "میں یہاں مدد کے لیے ہوں۔ کبھی کبھی کاموں کو چھوٹے مراحل میں تقسیم کرنے سے چیزیں زیادہ قابل انتظام محسوس ہوتی ہیں۔",
            'angry': "میں سمجھتا ہوں کہ آپ مایوس ہیں۔ آئیے ان چیزوں پر توجہ مرکوز کریں جن پر ہم قابو پا سکتے ہیں۔",
            'anxious': "ایک گہرا سانس لیں۔ آئیے اپنے کاموں کو ترجیح دیں اور ایک وقت میں ایک سے نمٹیں۔",
            'excited': "یہ شاندار توانائی ہے! آئیے اسے کام مکمل کرنے میں لگائیں۔",
            'neutral': "کام کے لیے تیار ہیں؟ مجھے بتائیں کہ آپ کیا کرنا چاہتے ہیں۔"
        }

        return urdu_recommendations.get(mood, urdu_recommendations['neutral'])

    def analyze_mood_trend(self, mood_history: list[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze mood trend over time"""
        if not mood_history:
            return {
                'trend': 'unknown',
                'avg_confidence': 0.0,
                'dominant_mood': 'neutral',
                'mood_stability': 0.0
            }

        from collections import Counter

        moods = [m['mood'] for m in mood_history]
        confidences = [m['confidence'] for m in mood_history]

        # Calculate dominant mood
        mood_counter = Counter(moods)
        dominant_mood = mood_counter.most_common(1)[0][0]

        # Calculate mood stability (how often mood changes)
        changes = sum(1 for i in range(1, len(moods)) if moods[i] != moods[i-1])
        stability = 1.0 - (changes / len(moods)) if len(moods) > 1 else 1.0

        # Determine trend
        if len(mood_history) >= 3:
            recent_moods = moods[-3:]
            if all(m in ['happy', 'excited'] for m in recent_moods):
                trend = 'improving'
            elif all(m in ['sad', 'anxious', 'angry'] for m in recent_moods):
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'

        return {
            'trend': trend,
            'avg_confidence': sum(confidences) / len(confidences),
            'dominant_mood': dominant_mood,
            'mood_stability': stability,
            'mood_distribution': dict(mood_counter),
            'total_samples': len(mood_history)
        }
