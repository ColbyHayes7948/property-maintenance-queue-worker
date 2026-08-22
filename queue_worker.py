import json
import os
import time

import infrai

QUEUE_NAME = "maintenance"


def route_request(request):
    """Return the next safe action for a maintenance request."""
    if request["category"] == "water" or request["priority"] == "urgent":
        return "dispatch-immediately"
    if request["category"] == "inspection":
        return "schedule-inspection"
    return "place-in-maintenance-queue"


def publish_request(request):
    return infrai.queue.publish(queue=QUEUE_NAME, payload=request)


def consume_once():
    result = infrai.queue.consume(queue=QUEUE_NAME, max_messages=1, visibility_timeout=60)
    messages = result.get("messages") or []
    if not messages:
        return None
    message = messages[0]
    request = message["payload"]
    action = route_request(request)
    print(json.dumps({"request_id": request["request_id"], "action": action}))
    infrai.queue.ack(queue=QUEUE_NAME, message_id=message["message_id"])
    return action


if __name__ == "__main__":
    sample = {
        "request_id": "mr-1042",
        "category": "inspection",
        "priority": "routine",
        "tenant_document": "lease-1042.pdf",
        "reminder_date": "2026-08-15",
    }
    publish_request(sample)
    while consume_once() is None:
        time.sleep(2)
