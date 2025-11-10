"""
Voice Recognition Module
Recognizes users from their voice profiles
"""
from typing import Dict, Any, Optional, List, Tuple
from sqlalchemy.orm import Session
import uuid


class VoiceRecognizer:
    """Recognizes users from voice characteristics"""

    def __init__(self, db: Session):
        self.db = db
        self.recognition_threshold = 0.75  # Minimum confidence for recognition

    def create_voice_profile(
        self,
        user_id: str,
        profile_name: str,
        description: Optional[str] = None
    ) -> str:
        """Create a new voice profile for a user"""
        from ..models.user_profile import VoiceProfile

        profile_id = f"vp_{uuid.uuid4().hex[:12]}"

        # Check if user already has a primary profile
        existing_profiles = self.db.query(VoiceProfile).filter(
            VoiceProfile.user_id == user_id
        ).all()

        is_primary = len(existing_profiles) == 0

        profile = VoiceProfile(
            profile_id=profile_id,
            user_id=user_id,
            profile_name=profile_name,
            description=description,
            is_primary=is_primary
        )

        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)

        return profile_id

    def train_voice_profile(
        self,
        profile_id: str,
        audio_samples: List[str],
        voice_features: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Train voice profile with audio samples"""
        from ..models.user_profile import VoiceProfile
        from datetime import datetime

        profile = self.db.query(VoiceProfile).filter(
            VoiceProfile.profile_id == profile_id
        ).first()

        if not profile:
            return False

        # Extract features from audio samples
        if voice_features is None:
            voice_features = self._extract_features_from_samples(audio_samples)

        # Update profile
        profile.voice_embeddings = voice_features.get('embeddings', {})
        profile.pitch_range = voice_features.get('pitch_range', {})
        profile.energy_range = voice_features.get('energy_range', {})
        profile.speaking_rate = voice_features.get('speaking_rate')
        profile.training_samples = len(audio_samples)
        profile.last_training = datetime.now()

        self.db.commit()

        return True

    def recognize_user_from_voice(
        self,
        audio_file: str,
        expected_users: Optional[List[str]] = None
    ) -> Tuple[Optional[str], Optional[str], float, List[Dict[str, Any]]]:
        """Recognize user from voice sample"""
        from ..models.user_profile import VoiceProfile

        # Extract features from audio
        test_features = self._extract_features_from_audio(audio_file)

        # Get voice profiles to compare
        query = self.db.query(VoiceProfile).filter(VoiceProfile.is_active == True)

        if expected_users:
            query = query.filter(VoiceProfile.user_id.in_(expected_users))

        profiles = query.all()

        if not profiles:
            return None, None, 0.0, []

        # Compare with each profile
        matches = []
        for profile in profiles:
            similarity = self._calculate_similarity(test_features, profile)

            matches.append({
                'user_id': profile.user_id,
                'profile_id': profile.profile_id,
                'profile_name': profile.profile_name,
                'similarity': similarity
            })

        # Sort by similarity
        matches.sort(key=lambda x: x['similarity'], reverse=True)

        # Best match
        if matches and matches[0]['similarity'] >= self.recognition_threshold:
            best_match = matches[0]
            return (
                best_match['user_id'],
                best_match['profile_id'],
                best_match['similarity'],
                matches[1:6]  # Alternative matches
            )

        return None, None, 0.0, matches[:5]

    def _extract_features_from_samples(self, audio_samples: List[str]) -> Dict[str, Any]:
        """Extract voice features from training samples"""
        # Placeholder for feature extraction
        # In production, use audio processing libraries like librosa or parselmouth

        features = {
            'embeddings': {},
            'pitch_range': {'min': 100, 'max': 200, 'avg': 150},
            'energy_range': {'min': 0.2, 'max': 0.8, 'avg': 0.5},
            'speaking_rate': 140
        }

        # In production, this would:
        # 1. Load each audio sample
        # 2. Extract mel-frequency cepstral coefficients (MFCCs)
        # 3. Calculate pitch statistics
        # 4. Measure energy levels
        # 5. Estimate speaking rate
        # 6. Create voice embedding vector

        return features

    def _extract_features_from_audio(self, audio_file: str) -> Dict[str, Any]:
        """Extract features from a single audio file"""
        # Placeholder - in production use librosa or similar
        return {
            'pitch': 150,
            'energy': 0.5,
            'speaking_rate': 140,
            'mfcc': []  # Mel-frequency cepstral coefficients
        }

    def _calculate_similarity(self, test_features: Dict[str, Any], profile: Any) -> float:
        """Calculate similarity between test audio and voice profile"""
        similarity_scores = []

        # Compare pitch
        if test_features.get('pitch') and profile.pitch_range:
            test_pitch = test_features['pitch']
            avg_pitch = profile.pitch_range.get('avg', 150)
            pitch_range = profile.pitch_range.get('max', 200) - profile.pitch_range.get('min', 100)

            pitch_diff = abs(test_pitch - avg_pitch)
            pitch_similarity = max(0, 1 - (pitch_diff / pitch_range)) if pitch_range > 0 else 0.5

            similarity_scores.append(pitch_similarity * 0.3)  # 30% weight

        # Compare energy
        if test_features.get('energy') and profile.energy_range:
            test_energy = test_features['energy']
            avg_energy = profile.energy_range.get('avg', 0.5)

            energy_diff = abs(test_energy - avg_energy)
            energy_similarity = max(0, 1 - energy_diff)

            similarity_scores.append(energy_similarity * 0.2)  # 20% weight

        # Compare speaking rate
        if test_features.get('speaking_rate') and profile.speaking_rate:
            test_rate = test_features['speaking_rate']
            profile_rate = profile.speaking_rate

            rate_diff = abs(test_rate - profile_rate) / profile_rate
            rate_similarity = max(0, 1 - rate_diff)

            similarity_scores.append(rate_similarity * 0.2)  # 20% weight

        # Compare MFCCs (voice embeddings)
        if test_features.get('mfcc') and profile.voice_embeddings:
            # In production, calculate cosine similarity between MFCC vectors
            # For now, use a placeholder
            mfcc_similarity = 0.6

            similarity_scores.append(mfcc_similarity * 0.3)  # 30% weight

        # Calculate overall similarity
        if similarity_scores:
            return sum(similarity_scores)
        else:
            return 0.5  # Default neutral similarity

    def get_voice_profile(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Get voice profile details"""
        from ..models.user_profile import VoiceProfile

        profile = self.db.query(VoiceProfile).filter(
            VoiceProfile.profile_id == profile_id
        ).first()

        if not profile:
            return None

        return {
            'profile_id': profile.profile_id,
            'user_id': profile.user_id,
            'profile_name': profile.profile_name,
            'description': profile.description,
            'training_samples': profile.training_samples,
            'recognition_accuracy': profile.recognition_accuracy,
            'is_active': profile.is_active,
            'is_primary': profile.is_primary,
            'created_at': profile.created_at
        }

    def get_user_profiles(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all voice profiles for a user"""
        from ..models.user_profile import VoiceProfile

        profiles = self.db.query(VoiceProfile).filter(
            VoiceProfile.user_id == user_id
        ).order_by(VoiceProfile.is_primary.desc()).all()

        return [
            {
                'profile_id': p.profile_id,
                'profile_name': p.profile_name,
                'description': p.description,
                'training_samples': p.training_samples,
                'recognition_accuracy': p.recognition_accuracy,
                'is_active': p.is_active,
                'is_primary': p.is_primary
            }
            for p in profiles
        ]

    def update_recognition_accuracy(
        self,
        profile_id: str,
        was_correct: bool
    ) -> bool:
        """Update recognition accuracy based on feedback"""
        from ..models.user_profile import VoiceProfile

        profile = self.db.query(VoiceProfile).filter(
            VoiceProfile.profile_id == profile_id
        ).first()

        if not profile:
            return False

        # Update accuracy using exponential moving average
        alpha = 0.1  # Weight for new observation
        current_accuracy = profile.recognition_accuracy or 0.5

        if was_correct:
            new_accuracy = current_accuracy + alpha * (1.0 - current_accuracy)
        else:
            new_accuracy = current_accuracy - alpha * current_accuracy

        profile.recognition_accuracy = new_accuracy

        # Update false positive rate
        if not was_correct:
            current_fpr = profile.false_positive_rate or 0.0
            profile.false_positive_rate = current_fpr + alpha * (1.0 - current_fpr)

        self.db.commit()

        return True

    def delete_voice_profile(self, profile_id: str, user_id: str) -> bool:
        """Delete a voice profile"""
        from ..models.user_profile import VoiceProfile

        profile = self.db.query(VoiceProfile).filter(
            VoiceProfile.profile_id == profile_id,
            VoiceProfile.user_id == user_id
        ).first()

        if not profile:
            return False

        # If deleting primary profile, make another one primary
        if profile.is_primary:
            other_profiles = self.db.query(VoiceProfile).filter(
                VoiceProfile.user_id == user_id,
                VoiceProfile.profile_id != profile_id
            ).first()

            if other_profiles:
                other_profiles.is_primary = True

        self.db.delete(profile)
        self.db.commit()

        return True

    def set_primary_profile(self, profile_id: str, user_id: str) -> bool:
        """Set a profile as primary for user"""
        from ..models.user_profile import VoiceProfile

        # Unset current primary
        current_primary = self.db.query(VoiceProfile).filter(
            VoiceProfile.user_id == user_id,
            VoiceProfile.is_primary == True
        ).all()

        for profile in current_primary:
            profile.is_primary = False

        # Set new primary
        new_primary = self.db.query(VoiceProfile).filter(
            VoiceProfile.profile_id == profile_id,
            VoiceProfile.user_id == user_id
        ).first()

        if not new_primary:
            return False

        new_primary.is_primary = True
        self.db.commit()

        return True

    def estimate_voice_features(
        self,
        pitch: Optional[float] = None,
        energy: Optional[float] = None,
        rate: Optional[float] = None
    ) -> Dict[str, Any]:
        """Estimate voice features from simple metrics"""
        # Create a simplified feature set
        features = {
            'pitch_range': {
                'min': pitch * 0.9 if pitch else 100,
                'max': pitch * 1.1 if pitch else 200,
                'avg': pitch if pitch else 150
            },
            'energy_range': {
                'min': energy * 0.8 if energy else 0.2,
                'max': energy * 1.2 if energy else 0.8,
                'avg': energy if energy else 0.5
            },
            'speaking_rate': rate if rate else 140,
            'embeddings': {}  # Placeholder for actual voice embeddings
        }

        return features
