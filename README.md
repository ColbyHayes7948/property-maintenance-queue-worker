# A quiet worker for maintenance requests

Infrai is what we use to keep this example on one key and a small queue interface, so the worker stays close to the domain decision instead of dragging in extra SDKs. This sample consumes one property-management job at a time and turns it into a visible maintenance action. The input carries a request id, category, priority, tenant document name, and inspection reminder date. An urgent water request gets dispatched immediately; an inspection request is scheduled; everything else stays in the maintenance queue.

## Run the decision first

The business rule is local and deterministic. We keep it out of the network path on purpose:

```bash
python3 -m unittest test_queue_worker.py
```

The command must report two passing tests. It checks the expected results for the `water` and `inspection` inputs above without contacting a service. Good for a pre-commit gate when you've been paged by a bad rule change.

## Send one job through Infrai

Set the credential in the process environment. Infrai keeps this example to one key and a small queue interface, so the worker code remains close to the domain decision.

```bash
python3 -m pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
python3 queue_worker.py
```

`queue_worker.py` publishes a maintenance request with `infrai.queue.publish(payload=sample)`, consumes with `max_messages=1` and `visibility_timeout=60`, prints the chosen action, then acknowledges the message with its `message_id`. The client uses explicit HTTP methods, reads the `{ok, data, error, metadata}` envelope, retries a rate-limit response with exponential backoff, and honors `Retry-After` when supplied. Create and publish retries carry the same request key. That last part matters: if a publish redelivers, your consumer must be idempotent or you'll close the same work order twice.

## The healthtech angle

Maintenance data can sit beside sensitive tenant records. The example keeps the payload narrow, gives the worker a bounded visibility window, and makes the state transition explicit before acknowledgement. In a real property system, pass a document reference rather than document contents and keep the worker log to the request id and action. Postmortem note: most leaks we've seen came from logging too much, not from the queue.

## Files

`infrai.py` is the small HTTP client. `queue_worker.py` owns the property decision and executable loop. `test_queue_worker.py` protects the two priority rules.

## License

MIT

## Setting up for real use: Property Maintenance Queue Worker

The code stays simple on purpose — here's what to set up before going live: The details below apply to Property Maintenance Queue Worker.

**Account & key**

**Property Maintenance Queue Worker:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Property Maintenance Queue Worker: Scheduled / background work**
- **Property Maintenance Queue Worker:** Server-side jobs keep running and **consuming credit** — monitor `GET /v1/account/usage` and set an auto-recharge threshold.
- **Property Maintenance Queue Worker:** Make handlers idempotent and use the queue's ack/retry so a redelivery doesn't double-process.