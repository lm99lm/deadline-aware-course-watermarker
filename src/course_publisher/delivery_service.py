from datetime import datetime, timezone
from typing import Any

from .models import CourseDelivery, EducatorReport


def publish_course_image(
    delivery: CourseDelivery,
    watermarker: Any,
    now: datetime | None = None,
) -> EducatorReport:
    decided_at = now or datetime.now(timezone.utc)
    if delivery.learner_deadline <= decided_at:
        return EducatorReport(
            course_id=delivery.course_id,
            educator_id=delivery.educator_id,
            decision="deadline_passed",
            decided_at=decided_at,
        )

    image_result = watermarker.watermark(
        image=delivery.image,
        text=delivery.watermark_text,
        position=delivery.position,
        opacity=delivery.opacity,
        idempotency_key=f"course-image:{delivery.course_id}:{delivery.learner_deadline.isoformat()}",
    )
    return EducatorReport(
        course_id=delivery.course_id,
        educator_id=delivery.educator_id,
        decision="published",
        decided_at=decided_at,
        image_result=image_result,
    )
