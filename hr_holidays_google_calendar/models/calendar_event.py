from odoo import models
from odoo.addons.google_calendar.models.google_sync import TIMEOUT


class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    def _google_insert(self, google_service, values, timeout=TIMEOUT):
        # When hr_holidays creates a leave event it sets no_mail_to_attendees=True,
        # meaning Odoo itself must not notify attendees. Honour that restriction in
        # Google Calendar too by suppressing the sendUpdates notification.
        if self.env.context.get("no_mail_to_attendees"):
            self = self.with_context(send_updates=False)
        return super()._google_insert(google_service, values, timeout=timeout)
