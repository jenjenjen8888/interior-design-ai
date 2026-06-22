# Architecture

## System Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│   Next.js App   │────▶│   FastAPI       │────▶│   AI Provider   │
│   (Frontend)    │     │   (Backend)     │     │   (Together/    │
│                 │◀────│                 │◀────│    OpenAI/Local) │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                              │
                              ▼
                        ┌─────────────────┐
                        │   PostgreSQL    │
                        │   + S3 Storage  │
                        └─────────────────┘
```

## Key Design Decisions

### 1. Provider Abstraction (AI Service Layer)

The `AIService` class abstracts away the AI provider. All providers implement the same interface:
- `get_suggestion(message, image_base64)` → string

This means switching from Together AI to self-hosted is a config change:
```
MODEL_PROVIDER=local
```

### 2. Vision-Language Model Choice

Starting with **Llama-Vision** via Together AI because:
- Supports both text and image inputs
- Can be fine-tuned with LoRA
- Good quality/cost ratio for a startup phase
- Same model can be self-hosted later via vLLM

### 3. Fine-Tuning Strategy

Using **LoRA** (Low-Rank Adaptation):
- Trains only ~1-5% of model parameters
- Much cheaper and faster than full fine-tuning
- Produces a small adapter file that can be swapped
- Allows iterating quickly on different training data

### 4. Frontend Architecture

Next.js with App Router:
- Server-side rendering for fast initial load
- Responsive design works on mobile + desktop
- Image optimization built-in
- Easy to add auth later (NextAuth.js)

## Migration Path: Cloud → Self-Hosted

When ready to self-host:

1. Export fine-tuned model weights from Together AI
2. Set up GPU server (A100 or similar)
3. Deploy model with vLLM (OpenAI-compatible API)
4. Change `MODEL_PROVIDER=local` and `MODEL_NAME` in config
5. No frontend or backend code changes needed

## Data Flow

### Suggestion Request
1. User uploads image / types description in frontend
2. Frontend sends multipart form to `/api/v1/suggest`
3. Backend encodes image to base64
4. Backend calls AI provider with system prompt + user input
5. AI returns text suggestion
6. Backend returns structured response to frontend
7. Frontend renders suggestion in chat interface

### Training Pipeline
1. Collect interior design images + expert descriptions
2. Run `prepare_dataset.py` to format into JSONL
3. Run `train.py` to fine-tune via Together AI
4. Run `evaluate.py` to compare base vs fine-tuned
5. Update `FINE_TUNED_MODEL` in backend config
