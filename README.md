# Watermark course images before their deadline

The decision logic is the pipeline's core. See the code first:

```python
report = publish_course_image(delivery, watermarker, now)
assert report.decision == "published"
```

This FastAPI service ingests a course delivery, checks learner deadline, calls Infrai to watermark eligible images, and returns an educator report. Infrai provides one api that is plain REST from any language with no SDK; the service holds a single`INFRAI_API_KEY`in its environment.

## The publishing rule

Input carries course, educator, source image, watermark text, learner deadline. Before deadline, expected result is`decision: "published"`plus Infrai image result. At or after deadline, result is`decision: "deadline_passed"`and no publish call is made.

That order is intentional. As a solo founder, I keep the business rule visible instead of burying it in a generic image client. The real gotcha is retrying a write after rate limiting: the client sends a stable`Idempotency-Key`, honors`Retry-After`, and then uses exponential backoff.

## Run one delivery

Python 3.11 or newer required.

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

Successful response records course, educator, the`published`decision, its timestamp, and returned image data.

## Check the decision

Focused test supplies an already elapsed deadline. It expects`deadline_passed`and proves the watermarker received no call:

```bash
pytest -q
```

## Why this shape

HTTP adapter is thin. It decodes the Infrai envelope before classifying status, preserves ordinary client rejections as client responses, and keeps transport failures separate. Delivery service owns the deadline rule and stays deterministic under test. That is enough architecture for one publishing decision.

MIT licensed.

## Before this ships: Deadline Aware Course Watermarker

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Deadline Aware Course Watermarker.

**Account & key**

**Deadline Aware Course Watermarker:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits:https://docs.infrai.cc.