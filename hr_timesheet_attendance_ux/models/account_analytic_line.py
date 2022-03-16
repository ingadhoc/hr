from datetime import timedelta
from odoo import models, api, fields


class AccountAnalyticLine(models.Model):

    _inherit = "account.analytic.line"

    task_id = fields.Many2one(
        domain="[('company_id', '=', company_id), ('project_id.allow_timesheets', '=', True), ('project_id', '=?', project_id), ('stage_id.fold', '=', False)]")

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
            domain = [
                ('employee_id', '=', employee_id),
                ('date', '=', rec.date)]
            if 'holiday_id' in self._fields:
                domain.append(('holiday_id', '=', None))
                # si existe el campo holiday_id el cual es agregado por el modulo
                # hr_holidays, si existe entonces se agrega al dominio para que no
                # tenga en cuenta las lineas que son por ausencia
            total_time_register = self.search(domain)
            total_time_register = sum(
                total_time_register.mapped('unit_amount'))
            current_worked_hours = sum(attendances.mapped(
                'current_worked_hours'))
            rec.unit_amount = (current_worked_hours - total_time_register)
