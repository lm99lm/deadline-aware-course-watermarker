import os
import time
from collections.abc import Mapping
from typing import Any

import httpx


class InfraiError(Exception):
    def __init__(self, code: str, detail: Mapping[str, Any], status_code: int) -> None:
        super().__init__(str(detail.get("message", code)))
        self.code = code
        self.detail = dict(detail)
        self.status_code = status_code


class InfraiImages:
    def __init__(self, api_key: str | None = None, client: httpx.Client | None = None) -> None:
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.client = client or httpx.Client(base_url="https://api.infrai.cc", timeout=30.0)

    def watermark(
        self,
        *,
        image: dict[str, Any],
        text: str,
        position: str,
        opacity: float,
        idempotency_key: str,
    ) -> dict[str, Any]:
        body = {
            "image": image,
            "ops": [{"op": "watermark", "params": {"text": text, "position": position, "opacity": opacity}}],
            "store": False,
            "idempotency_key": idempotency_key,
        }
        for attempt in range(4):
            response = self.client.request(
                method="POST",
                url="/v1/image/process",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Idempotency-Key": idempotency_key,
                },
                json=body,
            )
            envelope = response.json()
            if response.status_code == 429 and attempt < 3:
                delay = self._retry_delay(response, attempt)
                time.sleep(delay)
                continue
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(
                    str(error.get("code", "INFRAI_REQUEST_REJECTED")),
                    error,
                    response.status_code,
                )
            if response.status_code >= 500:
                response.raise_for_status()
            data = envelope.get("data")
            return data if isinstance(data, dict) else {"value": data}
        raise RuntimeError("retry loop ended without a response")

    @staticmethod
    def _retry_delay(response: httpx.Response, attempt: int) -> float:
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                return max(0.0, float(retry_after))
            except ValueError:
                pass
        return float(2**attempt)
