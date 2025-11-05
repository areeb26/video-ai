# Veo Character Consistency API Documentation

Complete API reference for generating videos programmatically.

## Base URL

```
http://localhost:8000/api/v1
```

For production, replace with your deployed API URL.

## Authentication

Currently, the API doesn't require authentication. For production use, implement API keys or OAuth tokens.

---

## Quick Start: Generate a Video

Here's the simplest way to generate a video:

```bash
curl -X POST http://localhost:8000/api/v1/generation \
  -H "Content-Type: application/json" \
  -d '{
    "generation_type": "text_to_video",
    "prompt": "A person walking through a sunny park",
    "aspect_ratio": "16:9",
    "quality": "low"
  }'
```

Response:
```json
{
  "id": 1,
  "generation_type": "text_to_video",
  "status": "processing",
  "prompt": "A person walking through a sunny park",
  "aspect_ratio": "16:9",
  "quality": "low",
  "created_at": "2025-11-04T12:00:00Z"
}
```

---

## API Endpoints

### 1. Characters API

#### Create a Character

Create a character profile with physical traits and style locks.

**Endpoint:** `POST /characters`

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/characters \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alex Rivera",
    "age": 28,
    "body_shape": "athletic",
    "hair_color": "dark brown",
    "hair_style": "short wavy",
    "skin_tone": "medium",
    "eye_color": "green",
    "height": "tall",
    "color_palette": ["#2C3E50", "#E74C3C", "#ECF0F1"],
    "accessories": ["silver watch", "black glasses"],
    "negative_traits": ["different hair color", "wrong eye color"]
  }'
```

**Response:**
```json
{
  "id": 1,
  "stable_id": "char_a1b2c3d4e5f6",
  "name": "Alex Rivera",
  "age": 28,
  "body_shape": "athletic",
  "hair_color": "dark brown",
  "hair_style": "short wavy",
  "skin_tone": "medium",
  "eye_color": "green",
  "height": "tall",
  "color_palette": ["#2C3E50", "#E74C3C", "#ECF0F1"],
  "accessories": ["silver watch", "black glasses"],
  "negative_traits": ["different hair color", "wrong eye color"],
  "face_embedding": null,
  "created_at": "2025-11-04T12:00:00Z",
  "face_references": [],
  "outfits": []
}
```

#### Upload Face Reference

Upload 3-10 face reference images for character consistency.

**Endpoint:** `POST /characters/{character_id}/face-references`

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/characters/1/face-references \
  -F "file=@/path/to/face_image.jpg"
```

**Response:**
```json
{
  "message": "Face reference uploaded successfully",
  "reference_id": 1,
  "quality_score": 0.95
}
```

**Note:** Upload 3-10 images for best results. The system will automatically:
- Extract face embeddings
- Calculate quality scores
- Average embeddings for stable character representation

#### List All Characters

**Endpoint:** `GET /characters`

```bash
curl http://localhost:8000/api/v1/characters
```

#### Get Character Details

**Endpoint:** `GET /characters/{id}`

```bash
curl http://localhost:8000/api/v1/characters/1
```

#### Add Character Outfit

**Endpoint:** `POST /characters/{id}/outfits`

```bash
curl -X POST http://localhost:8000/api/v1/characters/1/outfits \
  -H "Content-Type: application/json" \
  -d '{
    "slot_name": "casual",
    "description": "Blue jeans, white t-shirt, sneakers",
    "top": "white cotton t-shirt",
    "bottom": "blue denim jeans",
    "shoes": "white sneakers",
    "accessories": ["watch", "sunglasses"],
    "colors": ["#FFFFFF", "#1E3A8A", "#000000"]
  }'
```

---

### 2. Video Generation API

#### Generate Video (Text-to-Video)

**Endpoint:** `POST /generation`

**Simple Text-to-Video:**
```bash
curl -X POST http://localhost:8000/api/v1/generation \
  -H "Content-Type: application/json" \
  -d '{
    "generation_type": "text_to_video",
    "prompt": "A person walking through a sunny park with trees",
    "aspect_ratio": "16:9",
    "quality": "low"
  }'
```

**With Character Consistency:**
```bash
curl -X POST http://localhost:8000/api/v1/generation \
  -H "Content-Type: application/json" \
  -d '{
    "generation_type": "text_to_video",
    "prompt": "Alex walking through a park, smiling at camera",
    "aspect_ratio": "16:9",
    "quality": "low",
    "character_id": 1,
    "style_locks": {
      "hair_color": "dark brown",
      "skin_tone": "medium",
      "eye_color": "green",
      "outfit": "casual blue jeans and white t-shirt"
    }
  }'
```

**Response:**
```json
{
  "id": 1,
  "generation_type": "text_to_video",
  "quality": "low",
  "prompt": "Alex walking through a park, smiling at camera",
  "aspect_ratio": "16:9",
  "character_id": 1,
  "status": "processing",
  "output_video_path": null,
  "created_at": "2025-11-04T12:00:00Z"
}
```

#### Generate Video (Image-to-Video)

**Endpoint:** `POST /generation`

```bash
curl -X POST http://localhost:8000/api/v1/generation \
  -H "Content-Type: application/json" \
  -d '{
    "generation_type": "image_to_video",
    "prompt": "Camera slowly zooms in on the person",
    "aspect_ratio": "16:9",
    "quality": "low",
    "input_image_path": "/path/to/input/image.jpg",
    "character_id": 1
  }'
```

#### Generate Video (Video-to-Video)

**Endpoint:** `POST /generation`

```bash
curl -X POST http://localhost:8000/api/v1/generation \
  -H "Content-Type: application/json" \
  -d '{
    "generation_type": "video_to_video",
    "prompt": "Transform the scene to golden hour lighting",
    "aspect_ratio": "16:9",
    "quality": "low",
    "input_video_path": "/path/to/input/video.mp4",
    "character_id": 1
  }'
```

#### Check Generation Status

**Endpoint:** `GET /generation/{id}`

```bash
curl http://localhost:8000/api/v1/generation/1
```

**Response (Processing):**
```json
{
  "id": 1,
  "status": "processing",
  "prompt": "Alex walking through a park",
  "output_video_path": null,
  "veo_job_id": "veo_abc123",
  "created_at": "2025-11-04T12:00:00Z",
  "started_at": "2025-11-04T12:00:05Z",
  "completed_at": null
}
```

**Response (Completed):**
```json
{
  "id": 1,
  "status": "completed",
  "prompt": "Alex walking through a park",
  "output_video_path": "https://storage.googleapis.com/.../video.mp4",
  "thumbnail_path": "https://storage.googleapis.com/.../thumb.jpg",
  "veo_job_id": "veo_abc123",
  "created_at": "2025-11-04T12:00:00Z",
  "started_at": "2025-11-04T12:00:05Z",
  "completed_at": "2025-11-04T12:02:30Z"
}
```

#### List All Generations

**Endpoint:** `GET /generation`

```bash
# All generations
curl http://localhost:8000/api/v1/generation

# Filter by status
curl "http://localhost:8000/api/v1/generation?status=completed"

# With pagination
curl "http://localhost:8000/api/v1/generation?skip=0&limit=10"
```

#### Validate Continuity

Check if a generated video maintains character consistency.

**Endpoint:** `POST /generation/{id}/validate-continuity`

```bash
curl -X POST http://localhost:8000/api/v1/generation/1/validate-continuity
```

**Response:**
```json
{
  "success": true,
  "continuity_score": {
    "face_similarity": 0.92,
    "face_consistency": 0.08,
    "overall_score": 0.89
  },
  "drift_flags": [],
  "frame_count": 5,
  "faces_detected": 5
}
```

---

### 3. Projects API

#### Create a Project

**Endpoint:** `POST /projects`

```bash
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Video Story",
    "description": "A short story about Alex in the park"
  }'
```

#### Create a Beat (Timeline Structure)

**Endpoint:** `POST /projects/{project_id}/beats`

```bash
curl -X POST http://localhost:8000/api/v1/projects/1/beats \
  -H "Content-Type: application/json" \
  -d '{
    "beat_type": "hook",
    "order": 1,
    "title": "Opening Scene",
    "description": "Establish the character and setting"
  }'
```

**Beat Types:** `hook`, `conflict`, `resolution`, `custom`

#### Create a Shot

**Endpoint:** `POST /projects/beats/{beat_id}/shots`

```bash
curl -X POST http://localhost:8000/api/v1/projects/beats/1/shots \
  -H "Content-Type: application/json" \
  -d '{
    "order": 1,
    "shot_type": "wide",
    "camera_path": "dolly",
    "aspect_ratio": "16:9",
    "character_id": 1,
    "character_prompt": "Alex Rivera in casual outfit, smiling",
    "setting_prompt": "Sunny park with green trees and walking path",
    "action_prompt": "Walking towards camera slowly",
    "mood_prompt": "Happy, relaxed, peaceful morning",
    "camera_prompt": "Slow dolly in, following character"
  }'
```

**Shot Types:** `wide`, `medium`, `close`, `extreme_close`
**Camera Paths:** `dolly`, `pan`, `orbit`, `static`, `tilt`, `zoom`

#### Generate Video for a Shot

**Endpoint:** `POST /generation/shots/{shot_id}/generate`

```bash
curl -X POST "http://localhost:8000/api/v1/generation/shots/1/generate?quality=low"
```

This automatically:
- Uses the shot's combined prompt
- Applies character face embeddings
- Enforces style locks
- Creates a shot version for tracking

---

## Parameters Reference

### Aspect Ratios
- `9:16` - Vertical (Instagram Stories, TikTok)
- `1:1` - Square (Instagram Feed)
- `16:9` - Horizontal (YouTube, standard video)
- `4:5` - Portrait (Instagram Feed)

### Quality Options
- `low` - Quick preview, lower resolution
- `high` - Final 4K render (takes longer)

### Generation Types
- `text_to_video` - Generate from text prompt only
- `image_to_video` - Animate a static image
- `video_to_video` - Transform existing video

### Status Values
- `pending` - Queued for generation
- `processing` - Currently generating
- `completed` - Successfully completed
- `failed` - Generation failed (check error_message)

---

## Complete Workflow Example

Here's a complete workflow to generate a video with character consistency:

### Step 1: Create a Character

```bash
CHAR_RESPONSE=$(curl -X POST http://localhost:8000/api/v1/characters \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sarah Chen",
    "age": 25,
    "hair_color": "black",
    "eye_color": "brown",
    "skin_tone": "light tan"
  }')

CHAR_ID=$(echo $CHAR_RESPONSE | jq -r '.id')
echo "Created character ID: $CHAR_ID"
```

### Step 2: Upload Face References

```bash
for img in face1.jpg face2.jpg face3.jpg face4.jpg face5.jpg; do
  curl -X POST http://localhost:8000/api/v1/characters/$CHAR_ID/face-references \
    -F "file=@$img"
  echo "Uploaded $img"
done
```

### Step 3: Create a Project

```bash
PROJECT_RESPONSE=$(curl -X POST http://localhost:8000/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sarah'\''s Day",
    "description": "A day in the life"
  }')

PROJECT_ID=$(echo $PROJECT_RESPONSE | jq -r '.id')
echo "Created project ID: $PROJECT_ID"
```

### Step 4: Create Beats and Shots

```bash
# Create hook beat
BEAT_RESPONSE=$(curl -X POST http://localhost:8000/api/v1/projects/$PROJECT_ID/beats \
  -H "Content-Type: application/json" \
  -d '{
    "beat_type": "hook",
    "order": 1,
    "title": "Morning"
  }')

BEAT_ID=$(echo $BEAT_RESPONSE | jq -r '.id')

# Create shot
SHOT_RESPONSE=$(curl -X POST http://localhost:8000/api/v1/projects/beats/$BEAT_ID/shots \
  -H "Content-Type: application/json" \
  -d '{
    "order": 1,
    "shot_type": "medium",
    "camera_path": "static",
    "aspect_ratio": "16:9",
    "character_id": '$CHAR_ID',
    "character_prompt": "Sarah Chen smiling at camera",
    "setting_prompt": "Modern apartment, morning sunlight",
    "action_prompt": "Drinking coffee, looking at camera",
    "mood_prompt": "Peaceful, energetic morning"
  }')

SHOT_ID=$(echo $SHOT_RESPONSE | jq -r '.id')
```

### Step 5: Generate Video

```bash
GEN_RESPONSE=$(curl -X POST "http://localhost:8000/api/v1/generation/shots/$SHOT_ID/generate?quality=low")

GEN_ID=$(echo $GEN_RESPONSE | jq -r '.id')
echo "Generation ID: $GEN_ID"
```

### Step 6: Poll for Completion

```bash
while true; do
  STATUS_RESPONSE=$(curl -s http://localhost:8000/api/v1/generation/$GEN_ID)
  STATUS=$(echo $STATUS_RESPONSE | jq -r '.status')

  echo "Status: $STATUS"

  if [ "$STATUS" = "completed" ]; then
    VIDEO_URL=$(echo $STATUS_RESPONSE | jq -r '.output_video_path')
    echo "Video ready: $VIDEO_URL"
    break
  elif [ "$STATUS" = "failed" ]; then
    ERROR=$(echo $STATUS_RESPONSE | jq -r '.error_message')
    echo "Generation failed: $ERROR"
    break
  fi

  sleep 5
done
```

### Step 7: Validate Continuity

```bash
curl -X POST http://localhost:8000/api/v1/generation/$GEN_ID/validate-continuity | jq
```

---

## Python SDK Example

```python
import requests
import time

BASE_URL = "http://localhost:8000/api/v1"

class VeoAPI:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url

    def create_character(self, name, **traits):
        """Create a character profile"""
        data = {"name": name, **traits}
        response = requests.post(f"{self.base_url}/characters", json=data)
        return response.json()

    def upload_face_reference(self, character_id, image_path):
        """Upload face reference image"""
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                f"{self.base_url}/characters/{character_id}/face-references",
                files=files
            )
        return response.json()

    def generate_video(self, prompt, aspect_ratio="16:9", quality="low", character_id=None):
        """Generate a video"""
        data = {
            "generation_type": "text_to_video",
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "quality": quality
        }
        if character_id:
            data["character_id"] = character_id

        response = requests.post(f"{self.base_url}/generation", json=data)
        return response.json()

    def get_generation_status(self, generation_id):
        """Check generation status"""
        response = requests.get(f"{self.base_url}/generation/{generation_id}")
        return response.json()

    def wait_for_completion(self, generation_id, poll_interval=5):
        """Wait for video generation to complete"""
        while True:
            status = self.get_generation_status(generation_id)

            if status['status'] == 'completed':
                return status
            elif status['status'] == 'failed':
                raise Exception(f"Generation failed: {status.get('error_message')}")

            time.sleep(poll_interval)

# Usage
api = VeoAPI()

# Create character
character = api.create_character(
    name="John Doe",
    age=30,
    hair_color="brown",
    eye_color="blue"
)

# Upload face references
for i in range(1, 6):
    api.upload_face_reference(character['id'], f"face{i}.jpg")

# Generate video
generation = api.generate_video(
    prompt="John walking in a city street, smiling",
    aspect_ratio="16:9",
    quality="low",
    character_id=character['id']
)

# Wait for completion
result = api.wait_for_completion(generation['id'])
print(f"Video URL: {result['output_video_path']}")
```

---

## JavaScript/Node.js SDK Example

```javascript
const axios = require('axios');

class VeoAPI {
  constructor(baseURL = 'http://localhost:8000/api/v1') {
    this.client = axios.create({ baseURL });
  }

  async createCharacter(name, traits = {}) {
    const response = await this.client.post('/characters', { name, ...traits });
    return response.data;
  }

  async uploadFaceReference(characterId, imagePath) {
    const FormData = require('form-data');
    const fs = require('fs');

    const formData = new FormData();
    formData.append('file', fs.createReadStream(imagePath));

    const response = await this.client.post(
      `/characters/${characterId}/face-references`,
      formData,
      { headers: formData.getHeaders() }
    );
    return response.data;
  }

  async generateVideo(prompt, options = {}) {
    const data = {
      generation_type: 'text_to_video',
      prompt,
      aspect_ratio: options.aspectRatio || '16:9',
      quality: options.quality || 'low',
      character_id: options.characterId
    };

    const response = await this.client.post('/generation', data);
    return response.data;
  }

  async getGenerationStatus(generationId) {
    const response = await this.client.get(`/generation/${generationId}`);
    return response.data;
  }

  async waitForCompletion(generationId, pollInterval = 5000) {
    return new Promise((resolve, reject) => {
      const interval = setInterval(async () => {
        try {
          const status = await this.getGenerationStatus(generationId);

          if (status.status === 'completed') {
            clearInterval(interval);
            resolve(status);
          } else if (status.status === 'failed') {
            clearInterval(interval);
            reject(new Error(status.error_message));
          }
        } catch (error) {
          clearInterval(interval);
          reject(error);
        }
      }, pollInterval);
    });
  }
}

// Usage
(async () => {
  const api = new VeoAPI();

  // Create character
  const character = await api.createCharacter('Jane Smith', {
    age: 28,
    hair_color: 'blonde',
    eye_color: 'green'
  });

  // Upload face references
  for (let i = 1; i <= 5; i++) {
    await api.uploadFaceReference(character.id, `face${i}.jpg`);
  }

  // Generate video
  const generation = await api.generateVideo(
    'Jane walking on a beach at sunset',
    {
      aspectRatio: '16:9',
      quality: 'low',
      characterId: character.id
    }
  );

  // Wait for completion
  const result = await api.waitForCompletion(generation.id);
  console.log('Video URL:', result.output_video_path);
})();
```

---

## Error Handling

All endpoints return standard HTTP status codes:

- `200 OK` - Successful request
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

Error response format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Rate Limits

Currently, no rate limits are enforced. For production use, consider implementing:
- Rate limiting per API key
- Concurrent generation limits
- Storage quotas

---

## Best Practices

1. **Face References**: Upload 5-7 high-quality images for best results
2. **Quality Selection**: Use `low` quality for testing, `high` for final renders
3. **Prompt Engineering**: Be specific with prompts, include character details
4. **Polling**: Poll every 5-10 seconds when waiting for completion
5. **Error Handling**: Always check status and handle failures gracefully
6. **Character Reuse**: Use `stable_id` to reuse characters across projects

---

## Support

For issues or questions:
- GitHub Issues: [your-repo/issues]
- Email: support@example.com
- Documentation: [your-docs-site]

---

## API Changelog

### v1.0.0 (2025-11-04)
- Initial API release
- Character management
- Video generation (text, image, video-to-video)
- Project and timeline management
- Continuity validation
