# Emberglow Studio

> One-click YouTube video generation for creators

## What is this?

Emberglow Studio is a production-ready application that generates complete YouTube videos from a single topic. Give it an idea, and it creates everything: an engaging script, professional voiceover, visuals (stock footage or AI-generated images), a fully rendered video, thumbnail, and YouTube metadata ready to upload.

**NOTE:** All stock footage is crawled from copyright-free sources and can be freely used in YouTube videos without attribution requirements.

**Key capabilities:**
- Generate complete YouTube videos from a single topic
- Uses AI-generated images or crawls copyright-free stock footage for specific topic (videos and images)
- Creates professional thumbnails
- Generates metadata, video descriptions, and hashtags
- Download outputs in TXT format for easy copying
- Production-ready in a few minutes

Emberglow studio handles the entire production pipeline from concept to final export. While you can create videos on any topic, the system includes 100+ pre-set topics across popular niches to get you started quickly.

**NOTE:** If you need long-form YouTube videos (like documentaries, story narration, etc.), you can use these specialized tools I've also created:

- **[Emberglow Text-To-Speech](https://github.com/abotic/Emberglow-Text-To-Speech)** - Professional long-form narration with voice cloning
- **[Emberglow Story Factory](https://github.com/abotic/Emberglow-story-factory)** - Complete story generation with visual prompts
- **[Emberglow Animate](https://github.com/abotic/Emberglow-Animate)** - Bulk AI image generation for scene illustrations

These tools work together to create production-quality long-form content.

## What was the goal?

Creating quality YouTube content is time-intensive. You need script writing, voice recording (or expensive TTS services), video editing, asset sourcing, thumbnail design, and metadata optimization. A single 5-minute video can take 4-6 hours of work.

I wanted to automate the complete video production workflow while maintaining quality and creative control. The result is a system that can generate a production-ready YouTube video from script to final render with metadata in few minutes.


---

## Demo video (click to start)
[![Emberglow Studio](https://img.youtube.com/vi/E5cG84DNF-A/maxresdefault.jpg)](https://www.youtube.com/watch?v=E5cG84DNF-A)

---

## Features

### Video Generation
- **Dual Formats**: YouTube Shorts (30-60s) and Standard videos (2-4min)
- **Three Content Categories**: 
  - **Why**: Science explanations, psychology, biology (e.g., "Why does time move faster as you age?")
  - **What If**: Hypothetical scenarios (e.g., "What if gravity disappeared?")
  - **Hidden Truths**: Systems analysis, economics, psychology (e.g., "How casinos hack your brain")
- **Custom Topics**: Create videos on any topic (beta feature)
- **Curated Topic Library**: 100+ pre-written topics across all categories

### Content Pipeline
- **Script Generation**: AI-powered, optimized for voice narration
- **Voice Selection**: 7+ curated voices with category recommendations
- **Voice Testing**: Preview any voice before generation
- **Visual Modes**:
  - **AI Images**: Custom scene generation using state-of-the-art image models
  - **Stock Media**: HD videos and photos with intelligent search
- **Smart Rendering**: Variable intro pacing, automatic asset looping, 1080p output

### Production Features
- **YouTube Metadata**: Auto-generated titles, descriptions, tags, hashtags
- **Thumbnail Generation**: AI-generated or extracted from video
- **Multi-Generation**: Run up to 8 videos concurrently
- **Real-Time Progress**: Live updates for each generation phase
- **Project Management**: Organized video library with preview and download
- **Active Generation Recovery**: Resume if you close browser mid-generation
- **Download Formats**: TXT, MP4, JPG for easy integration with other tools
- **Style Presets**: 11 visual styles (Cinematic, Photographic, Anime, Fantasy, Digital Art, Comic Book, 3D Model, and more)
- **Manual Overrides**: Custom script formatting, disable auto-optimization

## Tech Stack

### Backend
- **Runtime**: Python 3.12+ with Flask
- **Video Processing**: MoviePy, Pillow, FFmpeg
- **Integrations**: AI text generation, voice synthesis, image generation, stock media APIs
- **Optimization**: Concurrent generation, resource monitoring

### Frontend  
- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS
- **Build**: Vite
- **Real-Time**: Server-Sent Events with auto-recovery

### Architecture
```
├── backend/
│   ├── client/              # API clients
│   │   └── openai_client.py
│   ├── core/                # Generation engine
│   │   ├── generator.py     # Main pipeline
│   │   ├── models.py        # Data models
│   │   └── __init__.py
│   ├── services/            # Business logic
│   │   ├── script_service.py
│   │   ├── audio_service.py
│   │   ├── asset_service.py # AI/stock visuals
│   │   ├── render_service.py
│   │   └── stability_service.py
│   ├── repositories/        # Data access
│   │   ├── progress_repository.py
│   │   └── file_repository.py
│   ├── routes/              # API endpoints
│   │   ├── api.py
│   │   ├── videos.py
│   │   └── frontend.py
│   └── utils/               # Helpers
│       ├── validation.py
│       ├── resource_monitor.py
│       └── stock_search.py
│
└── frontend/
    └── src/
        ├── components/
        │   ├── Dashboard.tsx
        │   ├── GenerationPanel.tsx
        │   ├── VideoLibrary.tsx
        │   ├── ActiveGenerations.tsx
        │   └── [selectors, modals]
        ├── services/
        │   └── api.ts
        ├── hooks/
        │   ├── useVideoGeneration.ts
        │   └── useDownload.ts
        └── contexts/
            └── AppContext.tsx
```

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- API keys for text generation, voice synthesis, stock media, and optionally AI image generation

### Installation

1. **Clone repository**
```bash
git clone https://github.com/yourusername/emberglow-studio.git
cd emberglow-studio
```

2. **Backend setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your API keys
```

3. **Frontend setup**
```bash
cd frontend
npm install
npm run build  # Builds to backend/static
```

4. **Run**
```bash
cd backend
python app.py
```

Open http://localhost:5002

### Docker Deployment

```bash
# Build
docker build -t emberglow-studio .

# Run
docker run -p 5002:5002 \
  --env-file .env \
  --gpus all \
  emberglow-studio
```

## Usage

### Generate Your First Video

1. **Choose Format**: Select Shorts or Standard
2. **Select Visual Mode**: AI Images or Stock Media
3. **Pick Content Source**: Curated topics or Custom
4. **Choose Category**: Why, What If, or Hidden Truths
5. **Select Topic**: Pick from list or write your own
6. **Choose Voice**: Test voices, select one
7. **Optional**: Adjust image style (AI mode only)
8. **Generate**: Click generate and watch progress

The system will:
- Generate an engaging script
- Create professional narration
- Gather or generate visuals
- Render the video with proper pacing
- Generate thumbnail
- Create YouTube metadata

### Voice Selection

Test voices before generating:
- Click speaker icon next to voice dropdown
- Listen to sample in your chosen format
- Voices are tagged with recommended categories

### Review & Download

Generated videos appear in the library:
- **Watch**: Preview in-browser
- **Download**: Get MP4 file
- **Metadata**: View/copy YouTube title, description, tags
- **Thumbnail**: Download custom thumbnail

### Multi-Generation Workflow

Queue multiple videos:
- System supports up to 8 concurrent generations
- Progress tracked individually
- Active generations resume if browser closed

## Environment Variables

### Backend Configuration

Create `.env` file in backend directory:

```env
# Required
OPENAI_API_KEY=your_text_generation_api_key
ELEVENLABS_API_KEY=your_voice_synthesis_api_key
PEXELS_API_KEY=your_stock_media_api_key

# Optional (required for AI image mode)
STABILITY_API_KEY=your_image_generation_api_key

# Optional Settings
MAX_CONCURRENT_VIDEOS=8
VIDEO_ENCODING_THREADS=4
ENCODING_PRESET=fast
```

### Frontend Configuration

Create `.env` file in frontend directory:

```env
VITE_API_URL=http://localhost:5002
```

## Architecture Highlights

### Script Generation

AI-powered script creation with category-specific prompts:
- Optimized word counts per format (shorts: 80-100 words, standard: 800-1000 words)
- Voice-narration optimized (no stage directions, clean prose)
- Special handling for country-comparison topics
- Automatic text normalization for pronunciation

### Voice Pipeline

Professional voice synthesis with:
- Chunk-based processing for long scripts (up to 9500 characters per chunk)
- Audio normalization and seamless stitching
- Multiple voice profiles with personality matching

### Visual Asset System

**AI Mode:**
- Scene-by-scene prompt generation from script
- Style consistency across entire video
- Parallel image generation with retry logic
- Automatic fallback to stock on failure

**Stock Mode:**
- AI-powered keyword extraction from script
- Parallel video/image downloads
- HD preference (1280-1920px)
- Intelligent search across multiple stock sources

### Rendering Engine

- Variable intro pacing (4 clips at 7s each, then configurable duration per clip)
- Automatic aspect ratio handling and center cropping
- Video looping for short clips (with compatibility fallback)
- Seamless audio synchronization
- H.264 encoding with configurable quality presets

### Progress Tracking

Real-time generation monitoring:
- In-memory progress maps with file persistence
- Polling updates every 3 seconds
- Auto-recovery on page refresh
- Graceful handling of tab switching
- Completion detection with auto-refresh

## Performance

Video generation completes in a few minutes depending on:
- Video format (Shorts vs Standard)
- Visual mode (Stock vs AI-generated)
- System resources

**Optimization features:**
- Stock mode is faster (no image generation required)
- Automatic resource monitoring prevents system overload
- Efficient memory management during rendering
- Concurrent generation support (up to 8 videos)

## Development

### Backend Development
```bash
cd backend
source venv/bin/activate
python app.py
```

The server runs with auto-reload enabled in development mode.

### Frontend Development
```bash
cd frontend
npm run dev
```

Development server with hot module replacement runs on http://localhost:3000

### Type Checking
```bash
# Frontend
cd frontend
npm run type-check

# Backend
cd backend
mypy app/
```

## API Endpoints

### Video Generation
```
POST /api/generate
Body: {
  topic: string
  category: string
  voice_id: string
  video_type: "shorts" | "standard"
  generation_mode: "stock" | "stability"
  style_preset: string
}
```

### Progress Tracking
```
GET /api/progress/{progress_id}
Response: {
  step: string
  percentage: number
  status: "processing" | "completed" | "error"
  details: string
}
```

### Video Library
```
GET /api/videos
Response: Array<{
  name: string
  video: string
  thumbnail: string
  size_mb: number
  duration: number
  created: number
  status: "completed" | "generating"
  video_type: "shorts" | "standard"
}>
```

### Video Management
```
DELETE /api/videos/{video_name}
GET /api/download/video/{video_name}
GET /api/download/thumbnail/{video_name}
GET /api/metadata/{video_name}
```

## Planned features

- A/B Testing Support: Generate multiple thumbnail variants for testing
- Custom voice cloning from user audio samples
- B-roll overlay system
- Advanced editing (trim, reorder clips)
- Multi-language support
- YouTube upload integration
- Analytics dashboard
- Template system for consistent branding

## Contributing

This is a hobby project, but improvements are welcome:

1. Fork repository
2. Create feature branch
3. Make changes with clear commits
4. Test thoroughly
5. Submit PR

Areas for help:
- Performance optimizations
- Video editing features
- UI/UX improvements
- Bug fixes
- Documentation

**NOTE**: For this hobby project, I opted for a simple file-based state management system to keep the architecture lightweight. In a production environment, I would evolve this by test coverage, implementing redis as a message broker to manage generation queue, better scalability, using a database etc.:

## License

MIT License

See LICENSE file for details.

---

For questions or issues, please open a GitHub issue.
