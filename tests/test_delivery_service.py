from datetime import datetime, timezone

from course_publisher.delivery_service import publish_course_image
from course_publisher.models import CourseDelivery


class RecordingWatermarker:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def watermark(self, **request: object) -> dict:
        self.calls.append(request)
        return {"id": "watermarked-course-image"}


def test_expired_delivery_is_reported_without_publishing() -> None:
    watermarker = RecordingWatermarker()
    delivery = CourseDelivery(
        course_id="python-101",
        image={"url": "https://cdn.example.edu/python-101/cover.png"},
        watermark_text="Northwind Learning",
        learner_deadline=datetime(2026, 9, 5, 12, tzinfo=timezone.utc),
        educator_id="educator-7",
    )

    report = publish_course_image(
        delivery,
        watermarker,
        now=datetime(2026, 9, 6, 12, tzinfo=timezone.utc),
    )

    assert report.decision == "deadline_passed"
    assert report.image_result is None
    assert watermarker.calls == []
