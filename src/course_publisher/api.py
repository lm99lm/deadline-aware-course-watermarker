from fastapi import FastAPI, HTTPException

from .delivery_service import publish_course_image
from .infrai_images import InfraiError, InfraiImages
from .models import CourseDelivery, EducatorReport

service = FastAPI(title="Course Image Publisher")


@service.post("/course-images/publish", response_model=EducatorReport)
def publish(delivery: CourseDelivery) -> EducatorReport:
    try:
        return publish_course_image(delivery, InfraiImages())
    except InfraiError as error:
        client_status = error.status_code if 400 <= error.status_code < 500 else 502
        raise HTTPException(
            status_code=client_status,
            detail={"code": error.code, "message": str(error)},
        ) from error

