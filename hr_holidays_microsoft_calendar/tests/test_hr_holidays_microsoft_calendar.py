from datetime import datetime

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHrHolidaysMicrosoftCalendar(TransactionCase):
    """
    Verifies that no_mail_to_attendees=True (set by hr_holidays when validating
    a leave) removes the attendees key from the Microsoft Graph API payload,
    preventing Outlook from sending invitation emails.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Attendee",
                "email": "attendee@test.com",
            }
        )
        cls.event = cls.env["calendar.event"].create(
            {
                "name": "Test Leave Event",
                "start": datetime(2025, 6, 20, 8, 0),
                "stop": datetime(2025, 6, 20, 18, 0),
                "partner_ids": [(4, cls.partner.id)],
                "need_sync": False,
            }
        )
        cls.fields_to_sync = cls.env["calendar.event"]._get_microsoft_synced_fields()

    def test_microsoft_values_excludes_attendees_when_no_mail_to_attendees(self):
        """attendees must be absent from the Graph API payload when no_mail_to_attendees=True."""
        values = self.event.with_context(no_mail_to_attendees=True)._microsoft_values(self.fields_to_sync)
        self.assertNotIn(
            "attendees",
            values,
            "Outlook payload must not include attendees when no_mail_to_attendees=True",
        )

    def test_microsoft_values_keeps_attendees_without_no_mail_to_attendees(self):
        """attendees must remain in the Graph API payload when no_mail_to_attendees is not set."""
        values = self.event._microsoft_values(self.fields_to_sync)
        self.assertIn(
            "attendees",
            values,
            "Outlook payload must include attendees when no_mail_to_attendees is absent",
        )
