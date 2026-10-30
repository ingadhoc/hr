from odoo import models


class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    # Odoo 20 still calls this with the old signature in google_event_sync.py:68
    # (no `calendar`), so the override forwards whatever it gets instead of binding it.
    def _google_insert(self, *args, **kwargs):
        # When hr_holidays creates a leave event it sets no_mail_to_attendees=True,
        # meaning Odoo itself must not notify attendees. Honour that restriction in
        # Google Calendar too by suppressing the sendUpdates notification.
        if self.env.context.get("no_mail_to_attendees"):
            self = self.with_context(send_updates=False)
        return super()._google_insert(*args, **kwargs)
