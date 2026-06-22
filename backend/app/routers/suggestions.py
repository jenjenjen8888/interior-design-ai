import base64
from fastapi import APIRouter, File, Form, UploadFile
from pydantic import BaseModel
from typing import Optional

from app.services.ai_service import ai_service

router = APIRouter()


class SuggestionResponse(BaseModel):
    suggestion: str
    style: str
    references: list[str] = []


@router.post("/suggest", response_model=SuggestionResponse)
async def get_suggestion(
    message: str = Form(default=""),
    image: Optional[UploadFile] = File(default=None),
    style: str = Form(default="pinterest"),
):
    """Get interior design suggestions based on text and/or image input.
    
    Args:
        message: Text description of what the user wants
        image: Optional photo of their space
        style: Which model to use - "pinterest" (aspirational) or "stock" (polished/professional)
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

    return SuggestionResponse(suggestion=suggestion, style=style)
