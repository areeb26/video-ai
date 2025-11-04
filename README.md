# Veo Character Consistency App

A full-stack application for generating videos with character consistency using Google's Veo 3.1 model. Create character profiles with face embeddings, build story timelines, and generate videos with perfect character consistency across shots.

## Features

### Core Generation
- **Veo 3.1 Integration**: Connect your Google AI account for powerful video generation
- **Multiple Generation Modes**:
  - Text to video
  - Image to video
  - Video to video
- **Platform Presets**: One-click aspect ratios (9:16, 1:1, 16:9, 4:5)
- **Quality Options**: Low-res preview and final 4K rendering

### Character Consistency System
- **Character Profiles**: Create detailed character profiles with locked traits
  - Name, age, face refs, body shape, clothing set, color palette, accessories
- **Face Embeddings**: 3-10 reference images per character
- **Outfit Slots**: Multiple outfit configurations (casual, formal, hero, winter)
- **Pose and Expression Library**: Tied to character profiles
- **Negative Traits**: Prevent character drift
- **Global Style Locks**: Keep hair, skin tone, eyes, and outfit stable
- **Continuity Validator**: Flags drift between shots using similarity scores

### Timeline and Story Tools
- **Beat-Based Timeline**: Structure stories with hook, conflict, resolution
- **Shot List Builder**: Wide, medium, close, extreme close shots
- **Camera Path Presets**: Dolly, pan, orbit, tilt, zoom, static
- **Per-Beat Prompts**: Character, setting, action, mood, camera fields
- **Character Reuse**: Use stable character IDs across projects
- **Versioning**: Track and compare different versions of each shot

## Tech Stack

### Backend
- **FastAPI**: High-performance Python API framework
- **PostgreSQL**: Robust database for characters and projects
- **SQLAlchemy**: ORM for database operations
- **Google AI SDK**: Veo 3.1 integration
- **DeepFace**: Face recognition and embeddings
- **OpenCV**: Video processing and analysis

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **React Query**: Server state management
- **Zustand**: Client state management
- **shadcn/ui**: Beautiful UI components

## Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Google AI API key with Veo 3.1 access

### Backend Setup

1. **Install PostgreSQL** and create a database:
```bash
# On macOS
brew install postgresql
brew services start postgresql
createdb video_ai_db

# On Ubuntu/Debian
sudo apt-get install postgresql
sudo systemctl start postgresql
sudo -u postgres createdb video_ai_db
```

2. **Navigate to backend directory**:
```bash
cd backend
```

3. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

4. **Install dependencies**:
```bash
pip install -r requirements.txt
```

5. **Configure environment variables**:
```bash
cp .env.example .env
```

Edit `.env` and add your configuration:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/video_ai_db
GOOGLE_AI_API_KEY=your_google_ai_api_key_here
SECRET_KEY=your-secret-key-change-this-in-production
DEBUG=True
ALLOWED_ORIGINS=http://localhost:3000
```

6. **Create upload directories**:
```bash
mkdir -p uploads media
```

7. **Start the backend server**:
```bash
cd app
python main.py
```

The API will be available at `http://localhost:8000`
API docs at `http://localhost:8000/api/v1/docs`

### Frontend Setup

1. **Navigate to frontend directory**:
```bash
cd frontend
```

2. **Install dependencies**:
```bash
npm install
```

3. **Configure environment**:
```bash
cp .env.local.example .env.local
```

Edit `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

4. **Start the development server**:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Usage Guide

### 1. Create a Character

1. Go to **Characters** page
2. Click **New Character**
3. Fill in character details:
   - Name, age, physical traits
   - Hair color, eye color, skin tone
   - Body shape, height
   - Color palette and accessories
   - Negative traits to avoid

4. Upload 3-10 reference images of the character's face
5. Create outfit slots (casual, formal, hero, winter)

### 2. Create a Project

1. Go to **Projects** page
2. Click **New Project**
3. Add a name and description
4. Create **Beats** (hook, conflict, resolution)
5. For each beat, create **Shots**:
   - Select shot type (wide, medium, close)
   - Choose camera path (dolly, pan, orbit)
   - Assign a character
   - Fill in prompt fields:
     - Character description
     - Setting/location
     - Action happening
     - Mood/atmosphere
     - Camera movement details
   - Select aspect ratio

### 3. Generate Videos

#### Quick Generation
1. Go to **Generate** page
2. Enter a text prompt
3. Optionally select a character for consistency
4. Choose aspect ratio and quality
5. Click **Generate Video**

#### Shot-Based Generation
1. In a project, navigate to a shot
2. Click **Generate** on the shot
3. Choose quality (preview or 4K)
4. The system will:
   - Use the shot's combined prompt
   - Apply character's face embedding
   - Enforce style locks
   - Generate the video

### 4. Validate Continuity

1. After generation, click **Validate Continuity**
2. The system will:
   - Extract key frames from the video
   - Compare face embeddings
   - Calculate similarity scores
   - Flag any character drift
3. Review the continuity report:
   - Face similarity score
   - Face consistency across frames
   - Drift flags (if any)

## API Endpoints

### Characters
- `GET /api/v1/characters` - List all characters
- `POST /api/v1/characters` - Create a character
- `GET /api/v1/characters/{id}` - Get character details
- `PUT /api/v1/characters/{id}` - Update character
- `DELETE /api/v1/characters/{id}` - Delete character
- `POST /api/v1/characters/{id}/face-references` - Upload face reference
- `POST /api/v1/characters/{id}/outfits` - Add outfit

### Projects
- `GET /api/v1/projects` - List all projects
- `POST /api/v1/projects` - Create a project
- `GET /api/v1/projects/{id}` - Get project with beats and shots
- `PUT /api/v1/projects/{id}` - Update project
- `DELETE /api/v1/projects/{id}` - Delete project

### Beats
- `POST /api/v1/projects/{id}/beats` - Create beat
- `GET /api/v1/projects/{id}/beats` - List project beats
- `PUT /api/v1/projects/beats/{id}` - Update beat

### Shots
- `POST /api/v1/projects/beats/{id}/shots` - Create shot
- `GET /api/v1/projects/beats/{id}/shots` - List beat shots
- `PUT /api/v1/projects/shots/{id}` - Update shot

### Generation
- `POST /api/v1/generation` - Create video generation
- `GET /api/v1/generation` - List generations
- `GET /api/v1/generation/{id}` - Get generation details
- `POST /api/v1/generation/{id}/validate-continuity` - Validate continuity
- `POST /api/v1/generation/shots/{id}/generate` - Generate for specific shot

## Project Structure

```
video-ai/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── characters.py
│   │   │   ├── projects.py
│   │   │   └── generation.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── database.py
│   │   ├── models/
│   │   │   ├── character.py
│   │   │   ├── project.py
│   │   │   └── generation.py
│   │   ├── schemas/
│   │   │   ├── character.py
│   │   │   ├── project.py
│   │   │   └── generation.py
│   │   ├── services/
│   │   │   ├── veo_service.py
│   │   │   ├── face_embedding_service.py
│   │   │   └── continuity_validator.py
│   │   └── main.py
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── characters/
│   │   ├── projects/
│   │   ├── generation/
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   │   ├── ui/
│   │   └── navigation.tsx
│   ├── lib/
│   │   ├── api.ts
│   │   └── utils.ts
│   └── package.json
└── README.md
```

## Database Schema

### Characters
- Character profiles with stable IDs
- Physical traits and style locks
- Face embeddings (averaged from references)
- Negative traits to avoid

### Character Face References
- 3-10 images per character
- Individual embeddings with quality scores

### Character Outfits
- Multiple outfit slots per character
- Detailed descriptions and reference images

### Projects
- Story projects with metadata

### Beats
- Timeline beats (hook, conflict, resolution)
- Ordered within projects

### Shots
- Individual shots with camera settings
- Multi-field prompts (character, setting, action, mood, camera)
- Aspect ratio configuration

### Shot Versions
- Version tracking for each shot
- Continuity scores and drift flags

### Video Generations
- Generation jobs and status
- Input/output paths
- Character consistency data
- Veo API responses

## Tips for Best Results

### Character Consistency
1. **Use high-quality face references**: Clear, well-lit photos from multiple angles
2. **Include 5-7 reference images**: Balances quality and consistency
3. **Lock key traits**: Define hair color, eye color, skin tone explicitly
4. **Use negative traits**: Specify what to avoid (e.g., "different hair color", "wrong outfit")

### Prompt Engineering
1. **Be specific**: Detailed prompts yield better results
2. **Use the prompt fields**: Separate character, setting, action, mood, and camera
3. **Reference character traits**: Explicitly mention locked attributes in prompts
4. **Test with preview quality**: Iterate quickly before final 4K render

### Timeline Planning
1. **Start with beats**: Plan your story structure first
2. **Use varied shot types**: Mix wide, medium, and close shots
3. **Plan camera movement**: Choose appropriate camera paths for each shot
4. **Version your shots**: Generate multiple versions to find the best

### Continuity Validation
1. **Check after each shot**: Validate continuity immediately
2. **Watch for drift**: Pay attention to similarity scores below 0.7
3. **Regenerate if needed**: Use drift feedback to refine prompts
4. **Compare adjacent shots**: Ensure smooth transitions

## Troubleshooting

### Backend Issues

**Database connection error**:
- Check PostgreSQL is running: `pg_isready`
- Verify DATABASE_URL in `.env`
- Ensure database exists: `psql -l`

**Face detection failing**:
- Install system dependencies: `sudo apt-get install libgl1 libglib2.0-0`
- Check image quality and lighting
- Try different reference images

**Veo API errors**:
- Verify GOOGLE_AI_API_KEY is correct
- Check API quota and limits
- Ensure Veo 3.1 access is enabled

### Frontend Issues

**API connection error**:
- Check backend is running on port 8000
- Verify NEXT_PUBLIC_API_URL in `.env.local`
- Check browser console for CORS errors

**Build errors**:
- Delete `.next` folder: `rm -rf .next`
- Clear npm cache: `npm cache clean --force`
- Reinstall dependencies: `rm -rf node_modules && npm install`

## Development

### Running Tests
```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

### Code Formatting
```bash
# Backend
black app/
isort app/

# Frontend
npm run lint
npm run format
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: [your-repo/issues]
- Documentation: [your-docs-site]
- Email: support@example.com

## Roadmap

- [ ] Batch video generation
- [ ] Advanced pose library
- [ ] Character animation presets
- [ ] Multi-character scenes
- [ ] Voice synthesis integration
- [ ] Collaborative projects
- [ ] Cloud storage integration
- [ ] Mobile app
