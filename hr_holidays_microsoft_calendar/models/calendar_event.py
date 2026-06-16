from odoo import models


class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    def _microsoft_values(self, fields_to_sync, initial_values=()):
        # When hr_holidays creates a leave event it sets no_mail_to_attendees=True,
        # meaning Odoo itself must not notify attendees. Honour that restriction for
        # Outlook too by removing attendees from the Graph API payload so Microsoft
        # does not send invitation emails on its side.
        values = super()._microsoft_values(fields_to_sync, initial_values)
        if self.env.context.get("no_mail_to_attendees"):
            values.pop("attendees", None)
        return values
