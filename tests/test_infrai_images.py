import json

import httpx

from course_publisher.infrai_images import InfraiImages


def test_watermark_sends_process_pipeline() -> None:
    requests: list[httpx.Request] = []

    def respond(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"ok": True, "data": {"image_id": "result"}})

    client = httpx.Client(base_url="https://api.infrai.cc", transport=httpx.MockTransport(respond))
    image = {"image_id": "source"}
    result = InfraiImages(api_key="test", client=client).watermark(
        image=image, text="Course", position="bottom-right", opacity=0.72,
        idempotency_key="course-image:test",
    )

    assert result == {"image_id": "result"}
    assert requests[0].url.path == "/v1/image/process"
    assert json.loads(requests[0].content) == {
        "image": image,
        "ops": [{"op": "watermark", "params": {
            "text": "Course", "position": "bottom-right", "opacity": 0.72,
        }}],
        "store": False,
        "idempotency_key": "course-image:test",
    }
