import httpx
from typing import Optional, Dict, Any
import random
import json
import os
from ..core.config import settings


class VeoService:
    """Service for interacting with Google Veo 3.1 API (Google AI Sandbox)"""

    def __init__(self):
        self.api_url = "https://aisandbox-pa.googleapis.com/v1/video:batchAsyncGenerateVideoText"
        self.bearer_token = settings.GOOGLE_AI_BEARER_TOKEN or settings.GOOGLE_AI_API_KEY

        # Load request template from JSON file
        template_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "veo_request_template.json"
        )

        with open(template_path, 'r') as f:
            self.request_template = json.load(f)

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
                "9:16": "VIDEO_ASPECT_RATIO_PORTRAIT",
                "1:1": "VIDEO_ASPECT_RATIO_SQUARE",
                "16:9": "VIDEO_ASPECT_RATIO_LANDSCAPE",
                "4:5": "VIDEO_ASPECT_RATIO_PORTRAIT",
            }

            # Determine model key based on quality and generation type
            if input_video:
                model_key = "veo_3_1_v2v_fast_ultra"
            elif input_image:
                model_key = "veo_3_1_i2v_fast_ultra"
            else:
                model_key = "veo_3_1_t2v_fast_ultra"

            # Generate random seed for reproducibility
            seed = random.randint(10000, 99999)

            # Load and customize request template
            request_body = json.loads(json.dumps(self.request_template))  # Deep copy

            # Replace placeholders in the template
            request_str = json.dumps(request_body)
            request_str = request_str.replace("{{PROMPT}}", enhanced_prompt)
            request_str = request_str.replace("{{ASPECT_RATIO}}", aspect_ratio_map.get(aspect_ratio, "VIDEO_ASPECT_RATIO_LANDSCAPE"))
            request_str = request_str.replace("{{SEED}}", str(seed))
            request_str = request_str.replace("{{MODEL_KEY}}", model_key)
            request_str = request_str.replace("{{SCENE_ID}}", f"scene-{seed}")
            request_body = json.loads(request_str)

            # Override seed in requests if it exists in template
            if "requests" in request_body and len(request_body["requests"]) > 0:
                request_body["requests"][0]["seed"] = seed
                request_body["requests"][0]["videoModelKey"] = model_key
                request_body["requests"][0]["aspectRatio"] = aspect_ratio_map.get(aspect_ratio, "VIDEO_ASPECT_RATIO_LANDSCAPE")
                if "textInput" in request_body["requests"][0]:
                    request_body["requests"][0]["textInput"]["prompt"] = enhanced_prompt
                if "metadata" in request_body["requests"][0]:
                    request_body["requests"][0]["metadata"]["sceneId"] = f"scene-{seed}"

            # Make API request
            headers = {
                "Authorization": f"Bearer {self.bearer_token}",
                "Content-Type": "application/json"
            }

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.api_url,
                    json=request_body,
                    headers=headers
                )

                if response.status_code != 200:
                    error_detail = response.text
                    return {
                        "success": False,
                        "error": f"API request failed: {response.status_code} - {error_detail}",
                    }

                response_data = response.json()

            # Extract job ID and status from response
            job_id = None
            if "responses" in response_data and len(response_data["responses"]) > 0:
                first_response = response_data["responses"][0]
                # The response may contain operation info
                if "name" in first_response:
                    job_id = first_response["name"]
                elif "metadata" in first_response:
                    job_id = first_response["metadata"].get("name")

            return {
                "success": True,
                "job_id": job_id or f"veo-{seed}",
                "status": "processing",
                "video_url": None,  # Will be available when job completes
                "seed": seed,
                "response": response_data,
                "request_sent": request_body,  # Include for debugging
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

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
            # TODO: Implement status checking endpoint
            # The actual endpoint for checking status may be different
            # For now, return a placeholder response

            return {
                "success": True,
                "status": "processing",  # or "completed", "failed"
                "video_url": None,
                "response": {},
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
