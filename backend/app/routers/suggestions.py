import base64
from fastapi import APIRouter, File, Form, UploadFile
from pydantic import BaseModel
from typing import Optional

from app.services.ai_service import ai_service
from app.services.image_service import image_service

router = APIRouter()


class SuggestionResponse(BaseModel):
    suggestion: str
    style: str
    image_url: Optional[str] = None
    references: list[str] = []


@router.post("/suggest", response_model=SuggestionResponse)
async def get_suggestion(
    message: str = Form(default=""),
    image: Optional[UploadFile] = File(default=None),
    style: str = Form(default="pinterest"),
    generate_image: str = Form(default="true"),
):
    """Get interior design suggestions based on text and/or image input.
    
    Args:
        message: Text description of what the user wants
        image: Optional photo of their space
        style: Which model to use - "pinterest" (aspirational) or "stock" (polished/professional)
        generate_image: Whether to generate a visualization ("true"/"false")
    """

    image_data = None
    if image:
        contents = await image.read()
        image_data = base64.b64encode(contents).decode("utf-8")

    suggestion = await ai_service.get_suggestion(
        message=message,
        image_base64=image_data,
        style=style,
    )

    # Generate an image if requested
    generated_url = None
    if generate_image.lower() == "true":
        generated_url = await image_service.generate_design_image(suggestion, style)

    return SuggestionResponse(
        suggestion=suggestion,
        style=style,
        image_url=generated_url,
    )
