"""
Fine-tune a vision-language model on Together AI using your Pinterest data.

Run this from home (corporate proxy blocks file uploads):
    python ml/finetune_together.py

Prerequisites:
    - Together AI API key in backend/.env (TOGETHER_API_KEY=...)
    - Training data at ml/data/pinterest/train.jsonl (already prepared)
    - pip install together python-dotenv

The script will:
1. Upload your training file
2. Start a fine-tuning job
3. Print the job ID for monitoring

Cost: ~$2-5 from your $10 Together credit (depends on model size)
Time: ~30-60 minutes for the job to complete
"""

import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from together import Together

# Load env
env_path = Path(__file__).parent.parent / "backend" / ".env"
load_dotenv(env_path)

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
if not TOGETHER_API_KEY:
    print("Error: TOGETHER_API_KEY not found in backend/.env")
    sys.exit(1)

# Config
TRAIN_FILE = Path(__file__).parent / "data" / "pinterest" / "train.jsonl"
BASE_MODEL = "meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo"  # Vision model that supports fine-tuning
MODEL_SUFFIX = "interior-design-pinterest-v1"
EPOCHS = 3
LEARNING_RATE = 1e-5
BATCH_SIZE = 4

def main():
    if not TRAIN_FILE.exists():
        print(f"Error: Training file not found: {TRAIN_FILE}")
        print("Run prepare_dataset.py first.")
        sys.exit(1)

    client = Together(api_key=TOGETHER_API_KEY)

    # Step 1: Upload training file
    print("=" * 60)
    print("Step 1: Uploading training data...")
    print("=" * 60)

    file_resp = client.files.upload(file=str(TRAIN_FILE), purpose="fine-tune")
    file_id = file_resp.id
    print(f"  File uploaded: {file_id}")
    print(f"  Size: {file_resp.bytes} bytes")

    # Step 2: Start fine-tuning job
    print("\n" + "=" * 60)
    print("Step 2: Starting fine-tuning job...")
    print("=" * 60)
    print(f"  Base model: {BASE_MODEL}")
    print(f"  Epochs: {EPOCHS}")
    print(f"  Learning rate: {LEARNING_RATE}")
    print(f"  Batch size: {BATCH_SIZE}")
    print(f"  Model suffix: {MODEL_SUFFIX}")

    job_resp = client.fine_tuning.create(
        training_file=file_id,
        model=BASE_MODEL,
        n_epochs=EPOCHS,
        learning_rate=LEARNING_RATE,
        batch_size=BATCH_SIZE,
        suffix=MODEL_SUFFIX,
    )

    job_id = job_resp.id
    print(f"\n  Job created: {job_id}")
    print(f"  Status: {job_resp.status}")

    # Step 3: Monitor (optional - can also check via API later)
    print("\n" + "=" * 60)
    print("Step 3: Monitoring progress...")
    print("=" * 60)
    print("  (Press Ctrl+C to stop monitoring — job continues in background)")
    print()

    try:
        while True:
            time.sleep(30)
            status = client.fine_tuning.retrieve(job_id)
            print(f"  Status: {status.status}", end="")
            if hasattr(status, 'events') and status.events:
                latest = status.events[-1]
                print(f" — {latest.message if hasattr(latest, 'message') else ''}", end="")
            print()

            if status.status in ("completed", "failed", "cancelled"):
                break

    except KeyboardInterrupt:
        print("\n  Stopped monitoring. Job continues in background.")

    # Final status
    final = client.fine_tuning.retrieve(job_id)
    print(f"\n{'=' * 60}")
    print(f"Final status: {final.status}")

    if final.status == "completed":
        model_name = final.output_name if hasattr(final, 'output_name') else f"{TOGETHER_API_KEY[:8]}.../{MODEL_SUFFIX}"
        print(f"Fine-tuned model: {model_name}")
        print(f"\nTo use it, add this to backend/.env:")
        print(f"  PINTEREST_MODEL={model_name}")
        print(f"\nThen restart the backend and your suggestions will use the fine-tuned model!")
    elif final.status == "failed":
        print("Job failed. Check Together dashboard for details.")
        print(f"  https://api.together.ai/fine-tuning/{job_id}")


if __name__ == "__main__":
    main()
