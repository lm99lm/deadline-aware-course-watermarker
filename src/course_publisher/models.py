from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class CourseDelivery(BaseModel):
    course_id: str = Field(min_length=1)
    image: dict[str, Any]
    watermark_text: str = Field(min_length=1)
    learner_deadline: datetime
    educator_id: str = Field(min_length=1)
    position: str = "bottom-right"
    opacity: float = Field(default=0.72, ge=0, le=1)


class EducatorReport(BaseModel):
    course_id: str
    educator_id: str
    decision: Literal["published", "deadline_passed"]
    decided_at: datetime
    image_result: dict[str, Any] | None = None
