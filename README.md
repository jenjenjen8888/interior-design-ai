# Interior Design AI

An AI-powered interior design assistant that provides personalized suggestions based on your space and style preferences.

## Quick Start (Personal Machine Setup)

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git (optional, for version control)

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY (or other provider key)
```

### 2. Test the API connection

```bash
cd backend
uvicorn app.main:app --reload
# Visit http://localhost:8000/health in your browser
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
# Visit http://localhost:3000
```

### 4. Full Stack (Docker)

```bash
docker-compose up
```

## Architecture

- **Frontend**: Next.js (React) — responsive web app for mobile and desktop
- **Backend**: Python/FastAPI — API server with AI inference
- **ML Pipeline**: Fine-tuning pipeline for vision-language models
- **AI Provider**: Claude (Anthropic) by default, switchable to Gemini, OpenAI, or Together AI

## Project Structure

```
├── frontend/          # Next.js web application
├── backend/           # FastAPI service
│   └── app/
│       ├── main.py          # App entry point
│       ├── config.py        # Settings from .env
│       ├── routers/         # API endpoints
│       └── services/        # AI service (provider abstraction)
├── ml/                # Training pipeline & model configs
│   ├── data/pinterest/      # Training data (images + JSONL)
│   ├── configs/             # Training configs per model
│   ├── scripts/             # Data prep & description generation
│   ├── train.py             # Fine-tuning script
│   └── evaluate.py          # Model evaluation
├── pinterest/         # Raw Pinterest photos (input for training)
├── docker/            # Container configurations
└── docs/              # Architecture docs
```

## Two-Model Architecture

The app supports two style models:
- **Pinterest Style** — trained on aspirational, curated Pinterest interiors
- **Stock Style** — trained on professional Adobe/stock photography (not yet trained)

Users toggle between them in the UI. Until fine-tuned models are ready, both use the base model with style-specific prompts and your curated training descriptions as context.

## AI Providers

Switch providers by changing `MODEL_PROVIDER` in `backend/.env`:

| Provider | Best For | Vision | Cost |
|----------|----------|--------|------|
| `anthropic` | Production quality | Yes | ~$3/1M tokens |
| `gemini` | Free tier / prototyping | Yes | Free tier available |
| `together` | Fine-tuned models | Yes | ~$0.20/1M tokens |
| `openai` | Alternative | Yes | ~$0.15/1M tokens |

## Next Steps

1. ✅ Pinterest images collected (132 photos)
2. ✅ Descriptions generated via Claude Haiku (118 train / 14 val)
3. ⬜ Fine-tune model on Together AI (`python train.py --config configs/train_pinterest.yaml`)
4. ⬜ Collect stock/Adobe photos for second model
5. ⬜ Add user authentication
6. ⬜ Add suggestion history / saved designs
