import unittest

from queue_worker import route_request


class QueueWorkerDecisionTests(unittest.TestCase):
    def test_urgent_water_request_is_dispatched_immediately(self):
        request = {
            "request_id": "mr-1",
            "category": "water",
            "priority": "routine",
            "tenant_document": "lease-1.pdf",
            "reminder_date": "2026-08-15",
        }
        self.assertEqual(route_request(request), "dispatch-immediately")


    def test_inspection_request_becomes_a_scheduled_inspection(self):
        request = {
            "request_id": "mr-2",
            "category": "inspection",
            "priority": "routine",
            "tenant_document": "lease-2.pdf",
            "reminder_date": "2026-08-15",
        }
        self.assertEqual(route_request(request), "schedule-inspection")
