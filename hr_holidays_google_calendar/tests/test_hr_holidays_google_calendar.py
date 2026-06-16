from datetime import datetime
from unittest.mock import MagicMock, patch

from odoo.addons.google_calendar.models.google_sync import GoogleCalendarSync
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHrHolidaysGoogleCalendar(TransactionCase):
    """
    Verifies that no_mail_to_attendees=True (set by hr_holidays when validating
    a leave) propagates to _google_insert as send_updates=False, preventing
    Google Calendar from sending invitation emails to attendees.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.leave_type = cls.env["hr.leave.type"].create(
            {
                "name": "Paid Time Off Test",
                "requires_allocation": False,
                "create_calendar_meeting": True,
            }
        )
        cls.work_contact = cls.env["res.partner"].create(
            {
                "name": "Employee No User",
                "email": "employee.nouser@test.com",
            }
        )
        cls.employee_no_user = cls.env["hr.employee"].create(
            {
                "name": "Employee No User",
                "work_contact_id": cls.work_contact.id,
            }
        )

    def test_google_insert_suppresses_send_updates_when_no_mail_to_attendees(self):
        """no_mail_to_attendees=True must cause send_updates=False on _google_insert."""
        event = self.env["calendar.event"].create(
            {
                "name": "Test Leave Event",
                "start": datetime(2025, 6, 20, 8, 0),
                "stop": datetime(2025, 6, 20, 18, 0),
                "need_sync": False,
            }
        )
        captured_contexts = []

        def capture_context(model, service, values, **kwargs):
            captured_contexts.append(dict(model.env.context))

        with patch.object(GoogleCalendarSync, "_google_insert", autospec=True, side_effect=capture_context):
            event.with_context(no_mail_to_attendees=True)._google_insert(MagicMock(), {"summary": "Test"})

        self.assertEqual(len(captured_contexts), 1)
        self.assertFalse(
            captured_contexts[0].get("send_updates", True),
            "send_updates must be False when no_mail_to_attendees=True",
        )

    def test_google_insert_does_not_force_send_updates_without_no_mail(self):
        """Without no_mail_to_attendees, _google_insert must not force send_updates=False."""
        event = self.env["calendar.event"].create(
            {
                "name": "Test Event No Flag",
                "start": datetime(2025, 6, 21, 8, 0),
                "stop": datetime(2025, 6, 21, 18, 0),
                "need_sync": False,
            }
        )
        captured_contexts = []

        def capture_context(model, service, values, **kwargs):
            captured_contexts.append(dict(model.env.context))

        with patch.object(GoogleCalendarSync, "_google_insert", autospec=True, side_effect=capture_context):
            event._google_insert(MagicMock(), {"summary": "Test"})

        self.assertEqual(len(captured_contexts), 1)
        self.assertNotIn(
            "send_updates",
            captured_contexts[0],
            "send_updates must not be injected when no_mail_to_attendees is absent",
        )
