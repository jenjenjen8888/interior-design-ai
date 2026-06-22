"""
Image Generation Service

Uses FLUX.1.1-pro via Together AI to generate interior design visualizations.
Claude first distills the suggestion into a concise, image-gen-optimized prompt,
then FLUX renders it.
"""

from typing import Optional

from app.config import settings


IMAGE_PROMPT_INSTRUCTION = """Based on the interior design suggestion below, write a concise image generation prompt (max 150 words) for creating a photorealistic interior design photo.

Focus on:
- Specific room type and layout
- Exact colors and materials (e.g. "warm oak flooring" not just "wood")
- Key furniture pieces and their style
- Lighting type and mood
- One or two hero details that make the space special

Format: Write it as a single descriptive paragraph. Start with "Interior design photograph:" and end with "editorial photography, natural lighting, wide angle, 4K"

Do NOT include any preamble, bullet points, or explanation. Just the prompt.

SUGGESTION:
{suggestion}"""


class ImageService:
    """Generate interior design images using FLUX via Together AI."""

    def __init__(self):
        self.image_model = "black-forest-labs/FLUX.1.1-pro"

    async def _generate_image_prompt(self, suggestion: str) -> str:
        """Use Claude to distill the suggestion into an optimized image prompt."""
        import anthropic

        client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

        response = await client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=200,
            temperature=0.3,
            messages=[{
                "role": "user",
                "content": IMAGE_PROMPT_INSTRUCTION.format(suggestion=suggestion[:1000]),
            }],
        )

        return response.content[0].text

    async def generate_design_image(
        self,
        suggestion: str,
        style: str = "pinterest",
    ) -> Optional[str]:
        """Generate a design visualization image.

        Args:
            suggestion: The text suggestion from Claude
            style: "pinterest" or "stock" aesthetic

        Returns:
            URL of the generated image, or None on failure
        """
        try:
            from together import Together

            # Step 1: Get optimized image prompt from Claude
            prompt = await self._generate_image_prompt(suggestion)

            # Add style modifier
            if style == "pinterest":
                prompt += " Trending Pinterest aesthetic, aspirational, visually curated."
            else:
                prompt += " Professionally staged, clean lines, magazine quality."

            # Step 2: Generate the image with FLUX
            client = Together(api_key=settings.together_api_key)

            response = client.images.generate(
                model=self.image_model,
                prompt=prompt,
                width=1024,
                height=768,
                steps=20,
                n=1,
            )

            if response.data and response.data[0].url:
                return response.data[0].url

            return None

        except Exception as e:
            print(f"Image generation error: {e}")
            return None


# Singleton
image_service = ImageService()
