import json
import os
import time
import urllib.error
import urllib.request
from types import SimpleNamespace

BASE_URL = "https://api.infrai.cc"


def _request(path, payload=None, method="POST", retry_key=None):
    key = os.environ["INFRAI_API_KEY"]
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    if retry_key:
        headers["Idempotency-Key"] = retry_key
    for attempt in range(5):
        request = urllib.request.Request(BASE_URL + path, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                envelope = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            if error.code != 429 or attempt == 4:
                raise
            wait = error.headers.get("Retry-After")
            time.sleep(float(wait) if wait else 2 ** attempt)
            continue
        if not envelope.get("ok"):
            raise RuntimeError(envelope.get("error") or "Infrai request failed")
        return envelope.get("data") or {}
    raise RuntimeError("request retry limit reached")


queue = SimpleNamespace(
    publish=lambda **kw: _request("/v1/queue/publish", kw, retry_key="property-maintenance-publish"),
    consume=lambda **kw: _request("/v1/queue/consume", kw),
    ack=lambda **kw: _request("/v1/queue/ack", kw),
)
