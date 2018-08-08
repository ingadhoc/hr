from odoo import fields, models, api, _


class HrTimesheetSheet(models.Model):
    _inherit = "hr_timesheet.sheet"

    total_attendance = fields.Float(
        compute='_compute_totals',
    )
    total_timesheet = fields.Float(
        compute='_compute_totals',
    )
    total_difference = fields.Float(
        'Difference',
        compute='_compute_totals',
    )
    theoretical_hours = fields.Float(
    )
    theoretical_difference = fields.Float(
        compute='_compute_theoretical_difference',
        store=True,
    )
    description = fields.Char(
    )
    note = fields.Text(
    )
    attendance_count = fields.Integer(
        compute='_compute_attendances',
    )
    attendance_ids = fields.One2many(
        'hr.attendance',
        compute='_compute_attendances',
    )

    @api.depends('employee_id', 'date_start', 'date_end')
    def _compute_attendances(self):
        for rec in self:
            rec.attendance_ids = rec.env['hr.attendance'].search([
                ('employee_id', '=', rec.employee_id.id),
                ('check_in', '>=', rec.date_start),
                ('check_out', '<=', rec.date_end),
            ])
            rec.attendance_count = len(rec.attendance_ids)

    @api.depends('timesheet_ids', 'attendance_ids')
    def _compute_totals(self):
        for rec in self:
            rec.total_timesheet = sum(
                rec.timesheet_ids.mapped('unit_amount'))
            rec.total_attendance = sum(
                rec.attendance_ids.mapped('worked_hours'))
            rec.total_difference = rec.total_attendance - rec.total_timesheet

    @api.multi
    @api.depends('theoretical_hours', 'total_timesheet')
    def _compute_theoretical_difference(self):
        for rec in self:
            rec.theoretical_difference = rec.total_timesheet - \
                rec.theoretical_hours

    @api.multi
    def get_employee_attendance(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Attendances'),
            'res_model': 'hr.attendance',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.attendance_ids.ids)],
            'context': {'search_default_employee_id': self.employee_id.id},
        }

    @api.multi
    def get_employee_attendance_timesheet_report(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('HR Timesheet/Attendance Report'),
            'res_model': 'hr.timesheet.attendance.report',
            'view_mode': 'pivot',
            'context': {
                'search_default_user_id': self.employee_id.user_id.id,
                'pivot_column_groupby': [],
                'pivot_measures': ['total_attendance', 'total_timesheet',
                                   'total_difference'],
                'pivot_row_groupby': ['user_id', 'date:day'],
            },
            'domain': [('date', '>=', self.date_start),
                       ('date', '<=', self.date_end)],
        }
