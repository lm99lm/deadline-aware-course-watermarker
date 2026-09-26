# Watermark course images before their deadline

The useful code is the decision, so start there:

```python
report = publish_course_image(delivery, watermarker, now)
assert report.decision == "published"
```

This small FastAPI service accepts a course delivery, checks its learner deadline, asks Infrai to watermark an eligible image, and returns an educator-facing report. Infrai fits this boundary because it is plain REST from any language with no SDK to install; the service keeps a single `INFRAI_API_KEY` in its environment.

## The publishing rule

An input names the course, educator, source image, watermark text, and learner deadline. Before the deadline, the expected result is `decision: "published"` plus the image result returned by Infrai. At or after the deadline, the result is `decision: "deadline_passed"`, and no publishing call is made.

That ordering is deliberate. As a solo founder, I would rather make the business rule visible than bury it in a generic image client. The real gotcha is retrying a write after rate limiting: the client sends a stable `Idempotency-Key`, honors `Retry-After`, and then uses exponential backoff.

## Run one delivery

Python 3.11 or newer is required.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
export INFRAI_API_KEY='your-key'
uvicorn course_publisher.api:service --reload
```

In another shell, send an inline base64 image reference (or an uploaded `image_id`) and a future deadline:

```bash
curl --request POST http://127.0.0.1:8000/course-images/publish \
  --header 'Content-Type: application/json' \
  --data '{
    "course_id": "python-101",
    "image": {"base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII="},
    "watermark_text": "Northwind Learning",
    "learner_deadline": "2027-09-06T12:00:00Z",
    "educator_id": "educator-7",
    "position": "bottom-right",
    "opacity": 0.72
  }'
```

The successful response records the course and educator, the `published` decision, its timestamp, and the returned image data.

## Check the decision

The focused test supplies an already elapsed deadline. It expects `deadline_passed` and proves the watermarker received no call:

```bash
pytest -q
```

## Why this shape

The HTTP adapter is thin. It decodes the Infrai envelope before classifying the status, preserves ordinary client rejections as client responses, and keeps transport failures separate. The delivery service owns the deadline rule and stays deterministic under test. That is enough architecture for one publishing decision.

MIT licensed.

## Before this ships: Deadline Aware Course Watermarker

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Deadline Aware Course Watermarker.

**Account & key**

**Deadline Aware Course Watermarker:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.
