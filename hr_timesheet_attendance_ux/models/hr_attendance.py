from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import models, fields


class HrAttendance(models.Model):

    _inherit = "hr.attendance"

    current_worked_hours = fields.Float(
        string="Service Hours",
        compute='_compute_current_worked_hours',
    )

    def _compute_current_worked_hours(self):
        for attendance in self:
            check_out_datetime = datetime.strptime(
                attendance.check_out or fields.Datetime.now(),
                DEFAULT_SERVER_DATETIME_FORMAT)
            check_in_datetime = datetime.strptime(
                attendance.check_in, DEFAULT_SERVER_DATETIME_FORMAT)
            delta = check_out_datetime - check_in_datetime
            attendance.current_worked_hours = delta.total_seconds() / 3600.0
