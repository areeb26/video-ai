from deepface import DeepFace
import numpy as np
from typing import List, Optional, Dict, Any
import cv2
from PIL import Image
import os


class FaceEmbeddingService:
    """Service for extracting and comparing face embeddings"""

    def __init__(self, model_name: str = "Facenet512"):
        """
        Initialize face embedding service

        Args:
            model_name: Model to use (Facenet512, VGG-Face, ArcFace, etc.)
        """
        self.model_name = model_name

    def extract_embedding(self, image_path: str) -> Optional[Dict[str, Any]]:
        """
        Extract face embedding from an image

        Args:
            image_path: Path to the image file

        Returns:
            Dict with embedding and quality score, or None if no face detected
        """
        try:
            # Extract face embedding using DeepFace
            embedding_objs = DeepFace.represent(
                img_path=image_path,
                model_name=self.model_name,
                enforce_detection=True,
                detector_backend="opencv",
            )

            if not embedding_objs:
                return None

            # Get the first face (highest confidence)
            embedding_obj = embedding_objs[0]
            embedding = embedding_obj["embedding"]

            # Calculate quality score based on face region size
            face_confidence = embedding_obj.get("face_confidence", 0.5)

            return {
                "embedding": embedding,
                "quality_score": face_confidence,
            }

        except Exception as e:
            print(f"Error extracting embedding from {image_path}: {str(e)}")
            return None

    def extract_multiple_embeddings(
        self, image_paths: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Extract embeddings from multiple images

        Args:
            image_paths: List of image file paths

        Returns:
            List of dicts with embeddings and quality scores
        """
        results = []
        for image_path in image_paths:
            result = self.extract_embedding(image_path)
            if result:
                results.append(
                    {
                        "image_path": image_path,
                        "embedding": result["embedding"],
                        "quality_score": result["quality_score"],
                    }
                )
        return results

    def average_embeddings(self, embeddings: List[List[float]]) -> List[float]:
        """
        Average multiple face embeddings to create a stable representation

        Args:
            embeddings: List of embedding vectors

        Returns:
            Averaged embedding vector
        """
        if not embeddings:
            return []

        # Convert to numpy array and average
        embeddings_array = np.array(embeddings)
        averaged = np.mean(embeddings_array, axis=0)

        # Normalize the averaged embedding
        normalized = averaged / np.linalg.norm(averaged)

        return normalized.tolist()

    def calculate_similarity(
        self, embedding1: List[float], embedding2: List[float]
    ) -> float:
        """
        Calculate cosine similarity between two embeddings

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Similarity score (0-1, higher is more similar)
        """
        if not embedding1 or not embedding2:
            return 0.0

        # Convert to numpy arrays
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)

        # Calculate cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        similarity = dot_product / (norm1 * norm2)

        # Convert to 0-1 range (cosine similarity is -1 to 1)
        similarity = (similarity + 1) / 2

        return float(similarity)

    def verify_faces(
        self, image_path1: str, image_path2: str, threshold: float = 0.4
    ) -> Dict[str, Any]:
        """
        Verify if two images contain the same person

        Args:
            image_path1: Path to first image
            image_path2: Path to second image
            threshold: Similarity threshold (lower = stricter)

        Returns:
            Dict with verification result and similarity score
        """
        try:
            result = DeepFace.verify(
                img1_path=image_path1,
                img2_path=image_path2,
                model_name=self.model_name,
                enforce_detection=True,
                detector_backend="opencv",
            )

            return {
                "verified": result["verified"],
                "similarity": 1 - result["distance"],  # Convert distance to similarity
                "threshold": threshold,
            }

        except Exception as e:
            print(f"Error verifying faces: {str(e)}")
            return {
                "verified": False,
                "similarity": 0.0,
                "threshold": threshold,
                "error": str(e),
            }

    def detect_face_attributes(self, image_path: str) -> Optional[Dict[str, Any]]:
        """
        Detect face attributes like age, gender, emotion, race

        Args:
            image_path: Path to the image file

        Returns:
            Dict with detected attributes or None
        """
        try:
            analysis = DeepFace.analyze(
                img_path=image_path,
                actions=["age", "gender", "race", "emotion"],
                enforce_detection=True,
                detector_backend="opencv",
            )

            if not analysis:
                return None

            # Get first face
            face_analysis = analysis[0] if isinstance(analysis, list) else analysis

            return {
                "age": face_analysis.get("age"),
                "gender": face_analysis.get("dominant_gender"),
                "race": face_analysis.get("dominant_race"),
                "emotion": face_analysis.get("dominant_emotion"),
            }

        except Exception as e:
            print(f"Error detecting face attributes: {str(e)}")
            return None

    def create_character_embedding(
        self, image_paths: List[str], min_quality: float = 0.3
    ) -> Optional[List[float]]:
        """
        Create a stable character embedding from multiple reference images

        Args:
            image_paths: List of reference image paths
            min_quality: Minimum quality score to include an embedding

        Returns:
            Averaged embedding vector or None if insufficient quality images
        """
        # Extract embeddings from all images
        results = self.extract_multiple_embeddings(image_paths)

        # Filter by quality
        high_quality_embeddings = [
            r["embedding"] for r in results if r["quality_score"] >= min_quality
        ]

        if not high_quality_embeddings:
            return None

        # Average the high-quality embeddings
        return self.average_embeddings(high_quality_embeddings)
