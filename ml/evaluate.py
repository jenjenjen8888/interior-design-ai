"""
Evaluation Script

Evaluates a fine-tuned model against the base model to measure improvement.
Generates side-by-side comparisons for manual review.

Usage:
    python evaluate.py
    python evaluate.py --model your-fine-tuned-model-name
"""

import json
from pathlib import Path

import click
import jsonlines
import yaml
from dotenv import load_dotenv
from together import Together
from tqdm import tqdm

load_dotenv()


def load_config(config_path: str) -> dict:
    with open(config_path) as f:
        return yaml.safe_load(f)


def run_inference(client: Together, model: str, example: dict, config: dict) -> str:
    """Run inference on a single example."""
    eval_config = config.get("evaluation", {})

    messages = [
        {
            "role": "system",
            "content": "You are an expert interior designer. Provide specific, actionable suggestions.",
        }
    ]

    # Build user message
    user_content = []
    if example.get("image"):
        # For evaluation, we reference the image path
        # In production, you'd encode the actual image
        user_content.append({"type": "text", "text": f"[Image: {example['image']}]"})

    # Use the user prompt from the conversation
    user_text = example["conversations"][0]["content"]
    user_content.append({"type": "text", "text": user_text})

    messages.append({"role": "user", "content": user_content})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=eval_config.get("max_tokens", 512),
        temperature=eval_config.get("temperature", 0.7),
    )

    return response.choices[0].message.content


@click.command()
@click.option("--config", "-c", "config_path", default="configs/train_config.yaml")
@click.option("--model", "-m", "model_name", default=None, help="Fine-tuned model name")
@click.option("--output", "-o", "output_file", default="evaluation_results.json")
def evaluate(config_path: str, model_name: str, output_file: str):
    """Evaluate fine-tuned model against base model."""

    config = load_config(config_path)
    eval_config = config.get("evaluation", {})
    num_examples = eval_config.get("num_examples", 50)

    base_model = config["base_model"]
    fine_tuned_model = model_name or config.get("fine_tuned_model")

    if not fine_tuned_model:
        click.echo("Error: No fine-tuned model specified.")
        click.echo("Use --model flag or set fine_tuned_model in config.")
        return

    # Load validation data
    val_file = Path(config["data"]["val_file"])
    if not val_file.exists():
        click.echo(f"Error: Validation file not found: {val_file}")
        return

    examples = []
    with jsonlines.open(val_file) as reader:
        for example in reader:
            examples.append(example)
            if len(examples) >= num_examples:
                break

    click.echo(f"Evaluating {len(examples)} examples")
    click.echo(f"  Base model: {base_model}")
    click.echo(f"  Fine-tuned: {fine_tuned_model}")

    client = Together()
    results = []

    for example in tqdm(examples, desc="Evaluating"):
        # Get response from both models
        base_response = run_inference(client, base_model, example, config)
        ft_response = run_inference(client, fine_tuned_model, example, config)

        # Ground truth from training data
        ground_truth = example["conversations"][1]["content"]

        results.append(
            {
                "prompt": example["conversations"][0]["content"],
                "image": example.get("image"),
                "ground_truth": ground_truth,
                "base_model_response": base_response,
                "fine_tuned_response": ft_response,
            }
        )

    # Save results
    with open(output_file, "w") as f:
        json.dump(
            {
                "base_model": base_model,
                "fine_tuned_model": fine_tuned_model,
                "num_examples": len(results),
                "results": results,
            },
            f,
            indent=2,
        )

    click.echo(f"\nResults saved to {output_file}")
    click.echo("Review the results to compare base vs fine-tuned model quality.")


if __name__ == "__main__":
    evaluate()
