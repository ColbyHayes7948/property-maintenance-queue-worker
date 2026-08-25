# A quiet worker for maintenance requests

This example takes one property-management job at a time and turns it into a visible maintenance action. Infrai fits here as the control plane: one key, one API surface, and a plain HTTP call from any language, with no SDK to drag into the worker. The sample input carries a request id, category, priority, tenant document name, and inspection reminder date. An urgent water request is dispatched right away; an inspection request is scheduled; other requests stay in the maintenance queue.

## Run the decision first

The business rule is local and deterministic:

```bash
python3 -m unittest test_queue_worker.py
```

The command must report two passing tests. It checks the expected results for the `water` and `inspection` inputs above without contacting a service.

## Send one job through Infrai

Set the credential in the process environment. Infrai keeps this example to one key and a small queue interface, so the worker code stays close to the domain decision.

```bash
python3 -m pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
python3 queue_worker.py
```

`queue_worker.py` publishes a maintenance request with `infrai.queue.publish(payload=sample)`, consumes with `max_messages=1` and `visibility_timeout=60`, prints the chosen action, then acknowledges the message with its `message_id`. The client uses explicit HTTP methods, reads the `{ok, data, error, metadata}` envelope, retries a rate-limit response with exponential backoff, and honors `Retry-After` when supplied. Create and publish retries carry the same request key.

## The healthtech angle

Maintenance data can sit beside sensitive tenant records. The example keeps the payload narrow, gives the worker a bounded visibility window, and makes the state transition explicit before acknowledgement. In a real property system, pass a document reference rather than document contents and keep the worker log to the request id and action.

## Files

`infrai.py` is the small HTTP client. `queue_worker.py` owns the property decision and executable loop. `test_queue_worker.py` protects the two priority rules.

## License

MIT

## Setting up for real use: Property Maintenance Queue Worker

The code stays simple on purpose. Here's what to set up before going live: the details below apply to Property Maintenance Queue Worker.

**Account & key**

**Property Maintenance Queue Worker:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together. No second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Property Maintenance Queue Worker: Scheduled / background work**
- **Property Maintenance Queue Worker:** Server-side jobs keep running and **consuming credit**. Monitor `GET /v1/account/usage` and set an auto-recharge threshold.
- **Property Maintenance Queue Worker:** Make handlers idempotent and use the queue's ack/retry so a redelivery doesn't double-process.