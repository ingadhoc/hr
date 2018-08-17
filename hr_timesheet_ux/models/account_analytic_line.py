from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo import fields, models, api


class AccountAnalyticLine(models.Model):

    _inherit = "account.analytic.line"

    @api.onchange('employee_id', 'date')
    def onchange_compute_hours(self):
        user_employee = self.default_get(
            ['employee_id', 'user_id']).get('employee_id')
        hr_attendance = self.env['hr.attendance']
        for rec in self:
            init = datetime.strptime(rec.date, DEFAULT_SERVER_DATE_FORMAT)
            end = init + timedelta(hours=23, minutes=59, seconds=59)
            employee_id = rec.employee_id.id or user_employee
            attendances = hr_attendance.search([
                ('employee_id', '=', employee_id),
                ('check_in', '>=', fields.Datetime.to_string(init)),
                ('check_in', '<=', fields.Datetime.to_string(end)),
            ])
            total_time_register = self.search([
                ('employee_id', '=', employee_id),
                ('date', '=', rec.date),
            ])
            total_time_register = sum(
                total_time_register.mapped('unit_amount'))
            current_worked_hours = sum(attendances.mapped(
                'current_worked_hours'))
            rec.unit_amount = (current_worked_hours - total_time_register)
