from datetime import timedelta
from odoo import models, api


class AccountAnalyticLine(models.Model):

    _inherit = "account.analytic.line"

    @api.onchange('employee_id', 'date')
    def onchange_compute_hours(self):
        user_employee = self.default_get(
            ['employee_id', 'user_id']).get('employee_id')
        hr_attendance = self.env['hr.attendance']
        for rec in self:
            end = rec.date + timedelta(hours=23, minutes=59, seconds=59)
            employee_id = rec.employee_id.id or user_employee
            attendances = hr_attendance.search([
                ('employee_id', '=', employee_id),
                ('check_in', '>=', rec.date),
                ('check_in', '<=', end),
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

    @api.onchange('project_id')
    def onchange_project_id(self):
        """ Only filter by tasks that are in not folded stages.
        """
        res = super().onchange_project_id()

        if isinstance(res, (dict,)) and res.get('domain', False):
            task_domain = res.get('domain').get('task_id', [])
            res['domain']['task_id'] = task_domain + [
                ('stage_id.fold', '=', False)]
        return res
