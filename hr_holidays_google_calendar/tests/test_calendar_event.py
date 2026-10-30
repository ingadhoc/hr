from datetime import timedelta
from unittest.mock import patch

from odoo import fields
from odoo.addons.google_calendar.models.google_event_sync import GoogleEventSync
from odoo.tests.common import TransactionCase


class TestCalendarEventGoogleInsert(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        now = fields.Datetime.now()
        cls.event = cls.env["calendar.event"].create(
            {
                "name": "Time off",
                "start": now,
                "stop": now + timedelta(hours=1),
            }
        )

    def _forward(self, context, *args, **kwargs):
        """Call the override with the parent replaced, and return what the parent got."""
        seen = []

        def _parent(records, *parent_args, **parent_kwargs):
            seen.append((records.env.context, parent_args, parent_kwargs))

        # Not autospec: after_commit wraps the parent, so autospec would enforce
        # its signature and reject the very call shape this test covers.
        with patch.object(GoogleEventSync, "_google_insert", _parent):
            self.event.with_context(**context)._google_insert(*args, **kwargs)
        self.assertEqual(len(seen), 1, "the override must call its parent exactly once")
        return seen[0]

    def test_google_insert_forwards_every_call_shape(self):
        """The override forwards each call Odoo 20 makes, and suppresses the Google
        notification only when hr_holidays asked not to notify the attendees.
        """
        service = self.env["google.service"]
        values = {"summary": "Time off"}

        with self.subTest("confirming a draft event does not break"):
            # google_calendar/models/google_event_sync.py:68 still calls without `calendar`
            context, args, kwargs = self._forward({}, service, values, timeout=3)
            self.assertEqual(args, (service, values))
            self.assertEqual(kwargs, {"timeout": 3})
            self.assertNotIn("send_updates", context)

        with self.subTest("the call with a calendar reaches the parent untouched"):
            context, args, kwargs = self._forward({}, service, "primary", values, timeout=3)
            self.assertEqual(args, (service, "primary", values))
            self.assertEqual(kwargs, {"timeout": 3})
            self.assertNotIn("send_updates", context)

        with self.subTest("an approved time off does not notify attendees on Google"):
            context, args, kwargs = self._forward({"no_mail_to_attendees": True}, service, "primary", values)
            self.assertFalse(context["send_updates"])
            self.assertEqual(args, (service, "primary", values))
