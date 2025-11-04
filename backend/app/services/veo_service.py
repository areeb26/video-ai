import google.genai as genai
from google.genai import types
from typing import Optional, Dict, Any
import asyncio
import os
from ..core.config import settings


class VeoService:
    """Service for interacting with Google Veo 3.1 API"""

    def __init__(self):
        self.client = genai.Client(api_key=settings.GOOGLE_AI_API_KEY)

    async def generate_video(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        quality: str = "low",
        input_image: Optional[str] = None,
        input_video: Optional[str] = None,
        character_embedding: Optional[list] = None,
        style_locks: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate video using Veo 3.1

        Args:
            prompt: Text prompt for video generation
            aspect_ratio: Video aspect ratio (9:16, 1:1, 16:9, 4:5)
            quality: 'low' for preview or 'high' for 4K
            input_image: Path to input image for image-to-video
            input_video: Path to input video for video-to-video
            character_embedding: Face embedding for character consistency
            style_locks: Style attributes to maintain

        Returns:
            Dict with generation results
        """
        try:
            # Enhance prompt with character consistency and style locks
            enhanced_prompt = self._enhance_prompt(
                prompt, character_embedding, style_locks
            )

            # Map aspect ratio to Veo format
            aspect_ratio_map = {
                "9:16": "9:16",
                "1:1": "1:1",
                "16:9": "16:9",
                "4:5": "4:5",
            }

            # Prepare generation config
            config = {
                "prompt": enhanced_prompt,
                "aspect_ratio": aspect_ratio_map.get(aspect_ratio, "16:9"),
            }

            # Add quality settings
            if quality == "high":
                config["quality"] = "4k"
            else:
                config["quality"] = "preview"

            # Handle different generation types
            if input_video:
                # Video-to-video
                response = await self._generate_video_to_video(config, input_video)
            elif input_image:
                # Image-to-video
                response = await self._generate_image_to_video(config, input_image)
            else:
                # Text-to-video
                response = await self._generate_text_to_video(config)

            return {
                "success": True,
                "job_id": response.get("job_id"),
                "status": response.get("status"),
                "video_url": response.get("video_url"),
                "response": response,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    async def _generate_text_to_video(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate video from text prompt"""
        try:
            # Use the Veo 3 model
            response = self.client.models.generate_video(
                model="veo-3",
                prompt=config["prompt"],
                config={
                    "aspect_ratio": config["aspect_ratio"],
                }
            )

            return {
                "job_id": getattr(response, "id", None),
                "status": "processing",
                "video_url": getattr(response, "video_url", None),
            }

        except Exception as e:
            raise Exception(f"Text-to-video generation failed: {str(e)}")

    async def _generate_image_to_video(
        self, config: Dict[str, Any], image_path: str
    ) -> Dict[str, Any]:
        """Generate video from image + prompt"""
        try:
            # Read image file
            with open(image_path, "rb") as f:
                image_data = f.read()

            response = self.client.models.generate_video(
                model="veo-3",
                prompt=config["prompt"],
                image=image_data,
                config={
                    "aspect_ratio": config["aspect_ratio"],
                }
            )

            return {
                "job_id": getattr(response, "id", None),
                "status": "processing",
                "video_url": getattr(response, "video_url", None),
            }

        except Exception as e:
            raise Exception(f"Image-to-video generation failed: {str(e)}")

    async def _generate_video_to_video(
        self, config: Dict[str, Any], video_path: str
    ) -> Dict[str, Any]:
        """Generate video from video + prompt"""
        try:
            # Read video file
            with open(video_path, "rb") as f:
                video_data = f.read()

            response = self.client.models.generate_video(
                model="veo-3",
                prompt=config["prompt"],
                video=video_data,
                config={
                    "aspect_ratio": config["aspect_ratio"],
                }
            )

            return {
                "job_id": getattr(response, "id", None),
                "status": "processing",
                "video_url": getattr(response, "video_url", None),
            }

        except Exception as e:
            raise Exception(f"Video-to-video generation failed: {str(e)}")

    def _enhance_prompt(
        self,
        prompt: str,
        character_embedding: Optional[list] = None,
        style_locks: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Enhance prompt with character consistency and style locks"""
        enhanced = prompt

        if style_locks:
            # Add style lock instructions
            style_parts = []

            if "hair_color" in style_locks:
                style_parts.append(f"with {style_locks['hair_color']} hair")
            if "skin_tone" in style_locks:
                style_parts.append(f"{style_locks['skin_tone']} skin tone")
            if "eye_color" in style_locks:
                style_parts.append(f"{style_locks['eye_color']} eyes")
            if "outfit" in style_locks:
                style_parts.append(f"wearing {style_locks['outfit']}")
            if "color_palette" in style_locks:
                colors = ", ".join(style_locks["color_palette"])
                style_parts.append(f"with color palette: {colors}")

            if style_parts:
                enhanced += f". Character details: {', '.join(style_parts)}"

            # Add negative traits if present
            if "negative_traits" in style_locks and style_locks["negative_traits"]:
                negative = ", ".join(style_locks["negative_traits"])
                enhanced += f". Avoid: {negative}"

        return enhanced

    async def check_generation_status(self, job_id: str) -> Dict[str, Any]:
        """Check the status of a video generation job"""
        try:
            # Poll for job status
            response = self.client.models.get_generation(job_id)

            return {
                "success": True,
                "status": getattr(response, "status", "unknown"),
                "video_url": getattr(response, "video_url", None),
                "response": response,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
