"""
Dataset Preparation Script

Converts your interior design images and descriptions into the JSONL format
required for fine-tuning. Supports multiple input formats:

1. Directory of images with a CSV/JSON metadata file
2. Directory of images with text files (same name as image)
3. Manual annotation mode (interactive)

Usage:
    python scripts/prepare_dataset.py --input ./raw_data --output ./data
"""

import json
import os
from pathlib import Path
from typing import Optional

import click
import jsonlines
from PIL import Image
from tqdm import tqdm


SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

# Prompt templates for generating training conversations
ANALYSIS_PROMPTS = [
    "Analyze this room and suggest improvements.",
    "What interior design suggestions do you have for this space?",
    "How could this room be improved from a design perspective?",
    "What changes would you recommend for this interior?",
    "Please evaluate this room's design and offer suggestions.",
]


def validate_image(image_path: Path, max_size_mb: int = 10) -> bool:
    """Check if an image is valid and within size limits."""
    try:
        size_mb = image_path.stat().st_size / (1024 * 1024)
        if size_mb > max_size_mb:
            return False
        with Image.open(image_path) as img:
            img.verify()
        return True
    except Exception:
        return False


def resize_image(image_path: Path, output_path: Path, max_dim: int = 1024) -> Path:
    """Resize image to fit within max dimensions while preserving aspect ratio."""
    with Image.open(image_path) as img:
        if img.mode != "RGB":
            img = img.convert("RGB")

        # Only resize if larger than max_dim
        if max(img.size) > max_dim:
            img.thumbnail((max_dim, max_dim), Image.LANCZOS)

        img.save(output_path, "JPEG", quality=85)
    return output_path


def create_training_example(
    image_relative_path: str,
    description: str,
    prompt_idx: int = 0,
) -> dict:
    """Create a single training example in conversation format."""
    prompt = ANALYSIS_PROMPTS[prompt_idx % len(ANALYSIS_PROMPTS)]

    return {
        "image": image_relative_path,
        "conversations": [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": description},
        ],
    }


@click.command()
@click.option("--input", "-i", "input_dir", required=True, help="Input directory with images")
@click.option("--output", "-o", "output_dir", default="data", help="Output directory")
@click.option("--metadata", "-m", "metadata_file", default=None, help="CSV/JSON metadata file")
@click.option("--val-split", default=0.1, help="Validation split ratio")
@click.option("--max-dim", default=1024, help="Max image dimension")
def prepare_dataset(
    input_dir: str,
    output_dir: str,
    metadata_file: Optional[str],
    val_split: float,
    max_dim: int,
):
    """Prepare training dataset from raw images and descriptions."""

    input_path = Path(input_dir)
    output_path = Path(output_dir)
    images_output = output_path / "images"
    images_output.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        click.echo(f"Error: Input directory '{input_dir}' does not exist.")
        return

    # Collect all images
    image_files = [
        f for f in input_path.rglob("*")
        if f.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS
    ]

    if not image_files:
        click.echo("No supported images found in input directory.")
        return

    click.echo(f"Found {len(image_files)} images")

    # Load metadata if provided
    descriptions = {}
    if metadata_file:
        meta_path = Path(metadata_file)
        if meta_path.suffix == ".json":
            with open(meta_path) as f:
                raw = json.load(f)
            # Support two formats:
            # 1. Flat dict: {"filename.jpg": "description", ...}
            # 2. Nested format from generate_descriptions.py:
            #    {"images": [{"filename": ..., "description": ..., "status": ...}]}
            if isinstance(raw, dict) and "images" in raw and isinstance(raw["images"], list):
                for item in raw["images"]:
                    if item.get("status") == "generated" and item.get("description"):
                        descriptions[item["filename"]] = item["description"]
            elif isinstance(raw, dict):
                descriptions = raw
        elif meta_path.suffix == ".csv":
            import csv
            with open(meta_path) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    descriptions[row["filename"]] = row["description"]

    # Process images and create examples
    examples = []
    for idx, img_path in enumerate(tqdm(image_files, desc="Processing images")):
        if not validate_image(img_path):
            click.echo(f"  Skipping invalid image: {img_path.name}")
            continue

        # Resize and save
        output_img_path = images_output / f"img_{idx:05d}.jpg"
        resize_image(img_path, output_img_path, max_dim)

        # Get description
        description = descriptions.get(img_path.name, "")

        # Check for companion text file
        if not description:
            txt_path = img_path.with_suffix(".txt")
            if txt_path.exists():
                description = txt_path.read_text().strip()

        if not description:
            # Skip images without descriptions for now
            # In production, you'd want to annotate these
            click.echo(f"  No description for: {img_path.name} (skipping)")
            continue

        relative_path = f"images/img_{idx:05d}.jpg"
        example = create_training_example(relative_path, description, idx)
        examples.append(example)

    if not examples:
        click.echo("No valid examples created. Ensure images have descriptions.")
        return

    # Split into train/val
    split_idx = int(len(examples) * (1 - val_split))
    train_examples = examples[:split_idx]
    val_examples = examples[split_idx:]

    # Write JSONL files
    train_file = output_path / "train.jsonl"
    val_file = output_path / "val.jsonl"

    with jsonlines.open(train_file, mode="w") as writer:
        writer.write_all(train_examples)

    with jsonlines.open(val_file, mode="w") as writer:
        writer.write_all(val_examples)

    # Write metadata
    metadata = {
        "total_examples": len(examples),
        "train_examples": len(train_examples),
        "val_examples": len(val_examples),
        "image_max_dim": max_dim,
        "source_dir": str(input_path),
    }

    with open(output_path / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    click.echo(f"\nDataset prepared successfully!")
    click.echo(f"  Train: {len(train_examples)} examples -> {train_file}")
    click.echo(f"  Val:   {len(val_examples)} examples -> {val_file}")


if __name__ == "__main__":
    prepare_dataset()
