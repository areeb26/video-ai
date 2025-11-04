from typing import List, Dict, Any, Optional
import cv2
import numpy as np
from .face_embedding_service import FaceEmbeddingService
import os
import tempfile


class ContinuityValidator:
    """Service for validating character continuity across shots"""

    def __init__(self):
        self.face_service = FaceEmbeddingService()

    def validate_shot_continuity(
        self,
        reference_embedding: List[float],
        shot_video_path: str,
        style_locks: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Validate continuity for a shot against reference character

        Args:
            reference_embedding: Reference character face embedding
            shot_video_path: Path to the generated video
            style_locks: Style attributes to check

        Returns:
            Dict with continuity scores and drift flags
        """
        try:
            # Extract frames from video
            frames = self._extract_key_frames(shot_video_path, num_frames=5)

            if not frames:
                return {
                    "success": False,
                    "error": "Could not extract frames from video",
                }

            # Calculate face similarity for each frame
            face_similarities = []

            for frame in frames:
                # Save frame temporarily
                temp_frame_path = self._save_temp_frame(frame)

                try:
                    # Extract embedding from frame
                    frame_result = self.face_service.extract_embedding(temp_frame_path)

                    if frame_result:
                        # Compare with reference
                        similarity = self.face_service.calculate_similarity(
                            reference_embedding, frame_result["embedding"]
                        )
                        face_similarities.append(similarity)

                finally:
                    # Clean up temp file
                    if os.path.exists(temp_frame_path):
                        os.remove(temp_frame_path)

            # Calculate overall face similarity score
            if face_similarities:
                face_similarity_score = float(np.mean(face_similarities))
                face_consistency = float(np.std(face_similarities))  # Lower is better
            else:
                face_similarity_score = 0.0
                face_consistency = 1.0

            # Detect drift flags
            drift_flags = self._detect_drift(
                face_similarity_score, face_consistency, style_locks
            )

            return {
                "success": True,
                "continuity_score": {
                    "face_similarity": face_similarity_score,
                    "face_consistency": face_consistency,
                    "overall_score": self._calculate_overall_score(
                        face_similarity_score, face_consistency
                    ),
                },
                "drift_flags": drift_flags,
                "frame_count": len(frames),
                "faces_detected": len(face_similarities),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def _extract_key_frames(
        self, video_path: str, num_frames: int = 5
    ) -> List[np.ndarray]:
        """Extract key frames from video for analysis"""
        try:
            cap = cv2.VideoCapture(video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            if total_frames == 0:
                return []

            # Calculate frame indices to extract (evenly spaced)
            frame_indices = np.linspace(
                0, total_frames - 1, min(num_frames, total_frames), dtype=int
            )

            frames = []
            for idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                if ret:
                    frames.append(frame)

            cap.release()
            return frames

        except Exception as e:
            print(f"Error extracting frames: {str(e)}")
            return []

    def _save_temp_frame(self, frame: np.ndarray) -> str:
        """Save frame to temporary file"""
        temp_file = tempfile.NamedTemporaryFile(
            suffix=".jpg", delete=False, dir=tempfile.gettempdir()
        )
        cv2.imwrite(temp_file.name, frame)
        return temp_file.name

    def _detect_drift(
        self,
        face_similarity: float,
        face_consistency: float,
        style_locks: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """Detect drift based on continuity scores"""
        drift_flags = []

        # Face similarity thresholds
        if face_similarity < 0.6:
            drift_flags.append("low_face_similarity")
        if face_similarity < 0.4:
            drift_flags.append("severe_face_drift")

        # Face consistency thresholds
        if face_consistency > 0.15:
            drift_flags.append("inconsistent_face_across_frames")

        # TODO: Add style lock validation
        # This would require more advanced computer vision to detect
        # hair color, outfit, etc. from video frames

        return drift_flags

    def _calculate_overall_score(
        self, face_similarity: float, face_consistency: float
    ) -> float:
        """Calculate overall continuity score (0-1)"""
        # Weight face similarity more heavily
        # Lower consistency is better, so invert it
        consistency_score = max(0, 1 - face_consistency)

        overall = (face_similarity * 0.7) + (consistency_score * 0.3)
        return float(np.clip(overall, 0, 1))

    def compare_shots(
        self, shot1_video_path: str, shot2_video_path: str
    ) -> Dict[str, Any]:
        """
        Compare continuity between two consecutive shots

        Args:
            shot1_video_path: Path to first shot video
            shot2_video_path: Path to second shot video

        Returns:
            Dict with comparison results
        """
        try:
            # Extract last frame from shot 1
            frames1 = self._extract_key_frames(shot1_video_path, num_frames=1)
            # Extract first frame from shot 2
            frames2 = self._extract_key_frames(shot2_video_path, num_frames=1)

            if not frames1 or not frames2:
                return {
                    "success": False,
                    "error": "Could not extract frames for comparison",
                }

            # Save frames temporarily
            temp_frame1 = self._save_temp_frame(frames1[0])
            temp_frame2 = self._save_temp_frame(frames2[0])

            try:
                # Compare faces between shots
                verification = self.face_service.verify_faces(
                    temp_frame1, temp_frame2, threshold=0.4
                )

                return {
                    "success": True,
                    "match": verification["verified"],
                    "similarity": verification["similarity"],
                    "continuity_maintained": verification["similarity"] > 0.7,
                }

            finally:
                # Clean up
                if os.path.exists(temp_frame1):
                    os.remove(temp_frame1)
                if os.path.exists(temp_frame2):
                    os.remove(temp_frame2)

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
