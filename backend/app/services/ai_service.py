"""
AI Service - Abstraction layer for model inference.

Currently uses Claude (Anthropic) for both vision analysis and text suggestions,
with your curated Pinterest interior design descriptions as style context.

Can be swapped to a fine-tuned model later by changing MODEL_PROVIDER in .env.
"""

import json
import random
from pathlib import Path
from typing import Optional

from app.config import settings


SYSTEM_PROMPT = """You are an expert interior designer with deep knowledge of:
- Color theory and palettes
- Furniture arrangement and spatial planning
- Design styles (modern, minimalist, bohemian, mid-century, Scandinavian, industrial, traditional, coastal, farmhouse, art deco, contemporary, transitional, etc.)
- Lighting design
- Material selection and textures
- Budget-conscious alternatives

When analyzing a room photo, describe what you see and provide specific, actionable suggestions.
When responding to style descriptions, give detailed recommendations with reasoning.

Always structure your response with:
1. A brief assessment of the current state or request
2. 3-5 specific suggestions with explanations
3. Optional: budget-friendly alternatives

Be warm, encouraging, and specific. Reference actual products, colors, or styles by name when possible."""

MODEL_CONTEXT = {
    "pinterest": (
        "\n\nYour aesthetic sensibility is informed by trending, aspirational interior design — "
        "the kind of curated, visually striking spaces people save and share on Pinterest. "
        "Lean into bold choices, layered textures, and statement pieces. "
        "Reference the style examples provided to maintain consistency with this aesthetic."
    ),
    "stock": (
        "\n\nYour aesthetic sensibility is informed by professionally staged interiors — "
        "clean, polished, and broadly appealing spaces seen in magazines and stock photography. "
        "Lean into timeless choices, balanced compositions, and mass-market accessibility."
    ),
}


def _load_style_examples(style: str, num_examples: int = 5) -> str:
    """Load a random sample of training descriptions as style context."""
    if style != "pinterest":
        return ""

    train_file = Path(__file__).parent.parent.parent.parent / "ml" / "data" / "pinterest" / "train.jsonl"
    if not train_file.exists():
        return ""

    examples = []
    with open(train_file, "r") as f:
        for line in f:
            data = json.loads(line)
            # Extract the assistant's description
            for conv in data.get("conversations", []):
                if conv["role"] == "assistant":
                    examples.append(conv["content"])

    if not examples:
        return ""

    # Pick a random sample to provide as style reference
    sampled = random.sample(examples, min(num_examples, len(examples)))

    context = "\n\nHere are examples of the interior design aesthetic and analysis style you should emulate:\n\n"
    for i, ex in enumerate(sampled, 1):
        # Truncate to keep context reasonable
        truncated = ex[:600] + "..." if len(ex) > 600 else ex
        context += f"--- Example {i} ---\n{truncated}\n\n"

    return context


class AIService:
    """Unified interface for AI model inference across providers."""

    def __init__(self):
        self.provider = settings.model_provider
        self.model = settings.model_name

    async def get_suggestion(
        self,
        message: str,
        image_base64: Optional[str] = None,
        style: str = "pinterest",
    ) -> str:
        """Get a design suggestion from the AI model."""

        if self.provider == "anthropic":
            return await self._anthropic_inference(message, image_base64, style)
        elif self.provider == "gemini":
            return await self._gemini_inference(message, image_base64, style)
        elif self.provider == "together":
            return await self._together_inference(message, image_base64, style)
        elif self.provider == "openai":
            return await self._openai_inference(message, image_base64, style)
        elif self.provider == "local":
            return await self._local_inference(message, image_base64, style)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    async def _anthropic_inference(
        self,
        message: str,
        image_base64: Optional[str],
        style: str,
    ) -> str:
        """Inference via Anthropic Claude API."""
        import anthropic

        client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

        # Build system prompt with style context and examples
        system = SYSTEM_PROMPT
        if style in MODEL_CONTEXT:
            system += MODEL_CONTEXT[style]
        system += _load_style_examples(style)

        # Build user message content
        content = []
        if image_base64:
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": image_base64,
                },
            })

        text = message or "Please analyze this room and suggest improvements."
        content.append({"type": "text", "text": text})

        response = await client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system,
            messages=[{"role": "user", "content": content}],
        )

        return response.content[0].text

    async def _gemini_inference(
        self,
        message: str,
        image_base64: Optional[str],
        style: str,
    ) -> str:
        """Inference via Google Gemini API."""
        import base64
        from google import genai

        client = genai.Client(api_key=settings.gemini_api_key)

        # Build system instruction
        system = SYSTEM_PROMPT
        if style in MODEL_CONTEXT:
            system += MODEL_CONTEXT[style]
        system += _load_style_examples(style)

        # Build content parts
        contents = []
        if image_base64:
            image_bytes = base64.b64decode(image_base64)
            contents.append(genai.types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"))

        text = message or "Please analyze this room and suggest improvements."
        contents.append(text)

        response = client.models.generate_content(
            model=self.model,
            contents=contents,
            config=genai.types.GenerateContentConfig(
                system_instruction=system,
                max_output_tokens=1024,
                temperature=0.7,
            ),
        )

        return response.text

    async def _together_inference(
        self,
        message: str,
        image_base64: Optional[str],
        style: str,
    ) -> str:
        """Inference via Together AI API (for fine-tuned models)."""
        from together import AsyncTogether

        client = AsyncTogether(api_key=settings.together_api_key)

        # Pick the right fine-tuned model
        model = self.model
        if style == "pinterest" and settings.pinterest_model:
            model = settings.pinterest_model
        elif style == "stock" and settings.stock_model:
            model = settings.stock_model

        system = SYSTEM_PROMPT
        if style in MODEL_CONTEXT:
            system += MODEL_CONTEXT[style]

        messages = [{"role": "system", "content": system}]

        user_content = []
        if image_base64:
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
            })

        text = message or "Please analyze this room and suggest improvements."
        user_content.append({"type": "text", "text": text})
        messages.append({"role": "user", "content": user_content})

        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=1024,
            temperature=0.7,
        )

        return response.choices[0].message.content

    async def _openai_inference(
        self,
        message: str,
        image_base64: Optional[str],
        style: str,
    ) -> str:
        """Inference via OpenAI API."""
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.openai_api_key)

        system = SYSTEM_PROMPT
        if style in MODEL_CONTEXT:
            system += MODEL_CONTEXT[style]

        messages = [{"role": "system", "content": system}]

        user_content = []
        if image_base64:
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
            })

        text = message or "Please analyze this room and suggest improvements."
        user_content.append({"type": "text", "text": text})
        messages.append({"role": "user", "content": user_content})

        response = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=1024,
            temperature=0.7,
        )

        return response.choices[0].message.content

    async def _local_inference(
        self,
        message: str,
        image_base64: Optional[str],
        style: str,
    ) -> str:
        """Inference via local model (vLLM/Ollama compatible OpenAI API)."""
        from openai import AsyncOpenAI

        client = AsyncOpenAI(
            base_url="http://localhost:8080/v1",
            api_key="not-needed",
        )

        system = SYSTEM_PROMPT
        if style in MODEL_CONTEXT:
            system += MODEL_CONTEXT[style]

        messages = [{"role": "system", "content": system}]

        user_content = []
        if image_base64:
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
            })

        text = message or "Please analyze this room and suggest improvements."
        user_content.append({"type": "text", "text": text})
        messages.append({"role": "user", "content": user_content})

        response = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=1024,
            temperature=0.7,
        )

        return response.choices[0].message.content


# Singleton instance
ai_service = AIService()
