"""
Training Script

Fine-tunes a vision-language model on interior design data using Together AI.
Supports LoRA fine-tuning for efficient training.

Usage:
    python train.py
    python train.py --config configs/train_config.yaml
"""

import json
import time
from pathlib import Path

import click
import yaml
from dotenv import load_dotenv
from together import Together

load_dotenv()


def load_config(config_path: str) -> dict:
    """Load training configuration from YAML file."""
    with open(config_path) as f:
        return yaml.safe_load(f)


def upload_dataset(client: Together, train_file: str, val_file: str) -> tuple[str, str]:
    """Upload training and validation files to Together AI."""
    print("Uploading training dataset...")
    train_response = client.files.upload(
        file=open(train_file, "rb"),
        purpose="fine-tune",
    )
    train_file_id = train_response.id
    print(f"  Train file uploaded: {train_file_id}")

    print("Uploading validation dataset...")
    val_response = client.files.upload(
        file=open(val_file, "rb"),
        purpose="fine-tune",
    )
    val_file_id = val_response.id
    print(f"  Val file uploaded: {val_file_id}")

    return train_file_id, val_file_id


def start_training(
    client: Together,
    config: dict,
    train_file_id: str,
    val_file_id: str,
) -> str:
    """Start a fine-tuning job on Together AI."""
    training_config = config["training"]
    together_config = config.get("together", {})

    print(f"\nStarting fine-tuning job...")
    print(f"  Base model: {config['base_model']}")
    print(f"  Epochs: {training_config['epochs']}")
    print(f"  Learning rate: {training_config['learning_rate']}")
    print(f"  LoRA rank: {training_config['lora_rank']}")

    response = client.fine_tuning.create(
        model=config["base_model"],
        training_file=train_file_id,
        validation_file=val_file_id,
        n_epochs=training_config["epochs"],
        learning_rate=training_config["learning_rate"],
        batch_size=training_config["batch_size"],
        warmup_ratio=training_config["warmup_ratio"],
        lora_rank=training_config["lora_rank"],
        lora_alpha=training_config["lora_alpha"],
        lora_dropout=training_config["lora_dropout"],
        suffix=together_config.get("model_suffix", "interior-design"),
    )

    job_id = response.id
    print(f"  Job started: {job_id}")
    return job_id


def monitor_training(client: Together, job_id: str) -> dict:
    """Monitor training job until completion."""
    print("\nMonitoring training progress...")

    while True:
        status = client.fine_tuning.retrieve(job_id)

        print(f"  Status: {status.status}", end="")
        if hasattr(status, "training_loss") and status.training_loss:
            print(f" | Loss: {status.training_loss:.4f}", end="")
        print()

        if status.status == "completed":
            print(f"\n Training complete!")
            print(f"  Fine-tuned model: {status.output_name}")
            return {
                "job_id": job_id,
                "model_name": status.output_name,
                "status": "completed",
            }
        elif status.status in ("failed", "cancelled"):
            print(f"\n Training {status.status}.")
            if hasattr(status, "error") and status.error:
                print(f"  Error: {status.error}")
            return {
                "job_id": job_id,
                "status": status.status,
                "error": getattr(status, "error", None),
            }

        time.sleep(30)  # Check every 30 seconds


@click.command()
@click.option(
    "--config",
    "-c",
    "config_path",
    default="configs/train_config.yaml",
    help="Path to training config",
)
@click.option("--monitor/--no-monitor", default=True, help="Monitor job until completion")
def train(config_path: str, monitor: bool):
    """Fine-tune a model on interior design data."""

    config = load_config(config_path)
    data_config = config["data"]

    # Validate dataset exists
    train_file = Path(data_config["train_file"])
    val_file = Path(data_config["val_file"])

    if not train_file.exists():
        click.echo(f"Error: Training file not found: {train_file}")
        click.echo("Run 'python scripts/prepare_dataset.py' first.")
        return

    if not val_file.exists():
        click.echo(f"Error: Validation file not found: {val_file}")
        return

    # Count examples
    with open(train_file) as f:
        train_count = sum(1 for _ in f)
    with open(val_file) as f:
        val_count = sum(1 for _ in f)

    click.echo(f"Dataset: {train_count} train, {val_count} val examples")

    if config.get("provider") == "together":
        client = Together()

        # Upload dataset
        train_file_id, val_file_id = upload_dataset(
            client, str(train_file), str(val_file)
        )

        # Start training
        job_id = start_training(client, config, train_file_id, val_file_id)

        # Save job info
        job_info = {
            "job_id": job_id,
            "config": config,
            "train_file_id": train_file_id,
            "val_file_id": val_file_id,
        }
        with open("training_job.json", "w") as f:
            json.dump(job_info, f, indent=2)

        # Monitor if requested
        if monitor:
            result = monitor_training(client, job_id)

            if result["status"] == "completed":
                click.echo(f"\nTo use your fine-tuned model, set in .env:")
                click.echo(f'  FINE_TUNED_MODEL={result["model_name"]}')
        else:
            click.echo(f"\nJob submitted. Check status with:")
            click.echo(f"  python train.py --check {job_id}")
    else:
        click.echo(f"Provider '{config.get('provider')}' not yet supported for training.")
        click.echo("Use 'together' provider for cloud fine-tuning.")


if __name__ == "__main__":
    train()
