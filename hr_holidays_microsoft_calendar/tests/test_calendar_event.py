from datetime import timedelta

from odoo import fields
from odoo.tests.common import TransactionCase


class TestCalendarEventMicrosoftValues(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        now = fields.Datetime.now()
        attendee = cls.env["res.partner"].create({"name": "Attendee", "email": "attendee@example.com"})
        cls.event = cls.env["calendar.event"].create(
            {
                "name": "Time off",
                "start": now,
                "stop": now + timedelta(hours=1),
                "partner_ids": [(6, 0, attendee.ids)],
            }
        )
        cls.synced_fields = cls.env["calendar.event"]._get_microsoft_synced_fields()

    def test_microsoft_values_keeps_attendees_on_a_regular_event(self):
        """Outside a time off nothing changes: Outlook still gets the attendees."""
        values = self.event._microsoft_values(self.synced_fields)
        self.assertTrue(values["attendees"])

    def test_microsoft_values_drops_attendees_for_a_time_off(self):
        """An approved time off reaches Outlook without attendees, so Microsoft does
        not send the invitation that hr_holidays asked to suppress.
        """
        event = self.event.with_context(no_mail_to_attendees=True)

        with self.subTest("the call microsoft_sync makes on create and on write"):
            values = event._microsoft_values(self.synced_fields)
            self.assertNotIn("attendees", values)
            self.assertEqual(values["subject"], "Time off")

        with self.subTest("the call calendar.recurrence makes for a series master"):
            values = event._microsoft_values(self.synced_fields, initial_values={"type": "seriesMaster"})
            self.assertNotIn("attendees", values)
            self.assertEqual(values["type"], "seriesMaster")
