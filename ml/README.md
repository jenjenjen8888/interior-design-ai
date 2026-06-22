# ML Training Pipeline

This directory contains the training pipeline for fine-tuning vision-language models on interior design data.

## Overview

We use **LoRA (Low-Rank Adaptation)** fine-tuning to teach a pre-trained vision-language model about interior design aesthetics, styles, and recommendations.

## Supported Base Models

- **Llama-Vision** (via Together AI) — good balance of quality and cost
- **LLaVA** — open-source, can be self-hosted later
- **GPT-4V** (via OpenAI) — highest quality, most expensive

## Dataset Format

Your training data should be organized as:

```
data/
├── images/           # Interior design photos
│   ├── img_001.jpg
│   ├── img_002.jpg
│   └── ...
├── train.jsonl       # Training examples
├── val.jsonl         # Validation examples
└── metadata.json     # Dataset info
```

Each JSONL line should follow this format:

```json
{
  "image": "images/img_001.jpg",
  "conversations": [
    {"role": "user", "content": "Analyze this room and suggest improvements."},
    {"role": "assistant", "content": "This is a modern living room with..."}
  ]
}
```

## Quick Start

1. Prepare your dataset (see `scripts/prepare_dataset.py`)
2. Configure training in `configs/train_config.yaml`
3. Run training: `python train.py`
4. Evaluate: `python evaluate.py`

## Training on Together AI

Together AI supports fine-tuning with LoRA. The pipeline handles:
- Dataset upload and validation
- Training job creation and monitoring
- Model evaluation and comparison
