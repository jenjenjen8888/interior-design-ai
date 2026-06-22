"""
Generate Descriptions Script

Uses a vision-language model to analyze each interior design photo and
generate a description covering:
- Room type (bedroom, living room, kitchen, etc.)
- Interior design style
- Color palette
- Key design elements
- Overall mood

Outputs a JSON file for review/editing before training.

Supports four providers:
  --provider anthropic (default model: claude-3-5-haiku-latest)
  --provider gemini    (default model: gemini-2.5-flash; free tier available)
  --provider openai    (default model: gpt-4o-mini)
  --provider together  (default model: meta-llama/Llama-4-Scout-17B-16E-Instruct)

Usage:
    python ml/scripts/generate_descriptions.py --input pinterest --output ml/descriptions_pinterest.json
    python ml/scripts/generate_descriptions.py --provider openai --input pinterest --output ml/descriptions_pinterest.json
"""

import base64
import json
import os
import time
from pathlib import Path

# Use the system trust store (picks up corporate CA certs on Windows/macOS).
# Must run before httpx/requests/genai imports so they pick it up.
try:
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

import click
from dotenv import load_dotenv
from tqdm import tqdm

# Load env from backend
env_path = Path(__file__).parent.parent.parent / "backend" / ".env"
load_dotenv(env_path)

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

DESCRIPTION_PROMPT = """Analyze this interior design photo and provide a detailed description. Include:

1. **Room Type**: What kind of room is this? (bedroom, living room, kitchen, bathroom, dining room, office, entryway, etc.)

2. **Interior Design Style**: What style best describes this space? (modern, minimalist, bohemian, mid-century modern, Scandinavian, industrial, traditional, coastal, farmhouse, art deco, contemporary, transitional, etc.)

3. **Color Palette**: List the primary colors used in the space, including walls, furniture, textiles, and accents.

4. **Key Design Elements**: What are the standout features? Consider furniture choices, lighting, textures, materials, artwork, plants, architectural details, and spatial arrangement.

5. **Overall Mood**: What feeling does this space evoke? (cozy, airy, dramatic, serene, energetic, luxurious, etc.)

Write your response as a cohesive paragraph (not bullet points) that flows naturally, as if you're describing this room to someone who wants to recreate the look. Be specific about colors, materials, and styles rather than generic."""


# Provider defaults
PROVIDER_DEFAULTS = {
    "anthropic": "claude-haiku-4-5",
    "gemini": "gemini-2.5-flash",
    "openai": "gpt-4o-mini",
    "together": "meta-llama/Llama-4-Scout-17B-16E-Instruct",
}


def encode_image(image_path: Path) -> str:
    """Read and base64-encode an image file."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def make_client(provider: str):
    """Build a vision client for the given provider."""
    if provider == "openai":
        from openai import OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY not found in environment. Add it to backend/.env"
            )
        return OpenAI(api_key=api_key)
    elif provider == "together":
        from together import Together
        api_key = os.getenv("TOGETHER_API_KEY")
        if not api_key:
            raise RuntimeError(
                "TOGETHER_API_KEY not found in environment. Add it to backend/.env"
            )
        return Together(api_key=api_key)
    elif provider == "gemini":
        from google import genai
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY not found in environment. "
                "Get one from https://aistudio.google.com/apikey "
                "and add it to backend/.env"
            )
        return genai.Client(api_key=api_key)
    elif provider == "anthropic":
        import anthropic
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY not found in environment. "
                "Get one from https://console.anthropic.com/settings/keys "
                "and add it to backend/.env"
            )
        return anthropic.Anthropic(api_key=api_key)
    else:
        raise ValueError(f"Unknown provider: {provider}")


def analyze_image(client, image_path: Path, image_base64: str, model: str, provider: str) -> str:
    """Send an image to the model and get a description."""
    # Detect mime type from extension (used by gemini and anthropic)
    ext = image_path.suffix.lower()
    mime = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }.get(ext, "image/jpeg")

    if provider == "gemini":
        from google.genai import types
        image_bytes = base64.b64decode(image_base64)
        response = client.models.generate_content(
            model=model,
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime),
                DESCRIPTION_PROMPT,
            ],
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=512,
            ),
        )
        return response.text

    if provider == "anthropic":
        response = client.messages.create(
            model=model,
            max_tokens=512,
            temperature=0.3,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": mime,
                                "data": image_base64,
                            },
                        },
                        {
                            "type": "text",
                            "text": DESCRIPTION_PROMPT,
                        },
                    ],
                }
            ],
        )
        return response.content[0].text

    # OpenAI + Together share an OpenAI-compatible chat completions API
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime};base64,{image_base64}"},
                    },
                    {
                        "type": "text",
                        "text": DESCRIPTION_PROMPT,
                    },
                ],
            }
        ],
        max_tokens=512,
        temperature=0.3,
    )
    return response.choices[0].message.content


@click.command()
@click.option("--input", "-i", "input_dir", required=True, help="Directory with images")
@click.option("--output", "-o", "output_file", default="descriptions_pinterest.json", help="Output JSON file")
@click.option(
    "--provider",
    "-p",
    type=click.Choice(["anthropic", "gemini", "openai", "together"]),
    default="anthropic",
    help="AI provider to use",
)
@click.option(
    "--model",
    "-m",
    "model_name",
    default=None,
    help="Model name (defaults to provider's recommended vision model)",
)
@click.option("--delay", "-d", "delay", default=1.0, help="Delay between API calls (seconds)")
@click.option("--resume/--no-resume", default=True, help="Resume from existing output file")
@click.option(
    "--limit",
    "-l",
    "limit",
    default=0,
    type=int,
    help="Max images to process this run (0 = all). Use with --resume to do batches.",
)
def generate_descriptions(
    input_dir: str,
    output_file: str,
    provider: str,
    model_name: str,
    delay: float,
    resume: bool,
    limit: int,
):
    """Generate descriptions for all images in a directory."""

    input_path = Path(input_dir)
    output_path = Path(output_file)

    if not input_path.exists():
        click.echo(f"Error: Input directory '{input_dir}' does not exist.")
        return

    # Default the model to the provider's recommended one
    if not model_name:
        model_name = PROVIDER_DEFAULTS[provider]

    try:
        client = make_client(provider)
    except RuntimeError as e:
        click.echo(f"Error: {e}")
        return

    # Collect all images
    image_files = sorted([
        f for f in input_path.iterdir()
        if f.suffix.lower() in SUPPORTED_EXTENSIONS
    ])

    if not image_files:
        click.echo("No supported images found.")
        return

    click.echo(f"Found {len(image_files)} images in {input_dir}")
    click.echo(f"Provider: {provider}")
    click.echo(f"Model: {model_name}")
    click.echo(f"Output: {output_file}")
    click.echo()

    # Load existing descriptions if resuming
    existing = {}
    if resume and output_path.exists():
        with open(output_path) as f:
            data = json.load(f)
            existing = {item["filename"]: item for item in data.get("images", [])}
        completed_count = sum(1 for v in existing.values() if v.get("status") == "generated")
        click.echo(f"Resuming: {completed_count} images already described")

    results = []
    errors = []
    processed_this_run = 0
    consecutive_errors = 0
    MAX_CONSECUTIVE_ERRORS = 5

    for img_path in tqdm(image_files, desc="Analyzing images"):
        filename = img_path.name

        # Skip if already described successfully
        if filename in existing and existing[filename].get("status") == "generated":
            results.append(existing[filename])
            continue

        # Stop if we've hit the per-run limit (counts attempts, not just successes)
        if limit > 0 and processed_this_run >= limit:
            click.echo(f"\nReached limit of {limit} images for this run. Re-run to continue.")
            break

        # Bail early if we hit too many consecutive errors (likely a config issue)
        if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
            click.echo(
                f"\nStopping: {MAX_CONSECUTIVE_ERRORS} consecutive errors. "
                "Check your model name / API key."
            )
            break

        processed_this_run += 1

        try:
            image_base64 = encode_image(img_path)
            description = analyze_image(client, img_path, image_base64, model_name, provider)

            results.append({
                "filename": filename,
                "description": description,
                "status": "generated",
            })
            consecutive_errors = 0

            # Save progress after each image (in case of interruption)
            output_data = {
                "provider": provider,
                "model_used": model_name,
                "total_images": len(image_files),
                "completed": len([r for r in results if r["status"] == "generated"]),
                "errors": len(errors),
                "images": results,
            }
            with open(output_path, "w") as f:
                json.dump(output_data, f, indent=2)

            # Rate limiting
            time.sleep(delay)

        except Exception as e:
            error_msg = str(e)
            click.echo(f"\n  Error on {filename}: {error_msg}")
            errors.append({"filename": filename, "error": error_msg})
            results.append({
                "filename": filename,
                "description": "",
                "status": "error",
                "error": error_msg,
            })
            consecutive_errors += 1
            # Longer delay on error (might be rate limited)
            time.sleep(delay * 3)

    # Final save
    output_data = {
        "provider": provider,
        "model_used": model_name,
        "total_images": len(image_files),
        "completed": len([r for r in results if r["status"] == "generated"]),
        "errors": len(errors),
        "images": results,
    }
    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=2)

    click.echo(f"\nDone!")
    click.echo(f"  Described: {output_data['completed']}/{len(image_files)} images")
    if errors:
        click.echo(f"  Errors: {len(errors)} (check output file)")
    click.echo(f"\nReview descriptions in: {output_file}")
    click.echo("Edit any descriptions you want to improve, then run the dataset preparation step.")


if __name__ == "__main__":
    generate_descriptions()
