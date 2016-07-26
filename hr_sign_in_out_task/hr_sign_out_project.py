# -*- coding: utf-8 -*-

from openerp import models, fields, api, _


class hr_sing_out_project(models.TransientModel):

    _inherit = 'hr.sign.out.project'

    task_id = fields.Many2one(
        'project.task',
        'Task')
    timesheet_task_required = fields.Boolean(
        related='account_id.project_id.timesheet_task_required')

    @api.model
    def _write(self, data, emp_id):
        timesheet_id = super(hr_sing_out_project, self)._write(data, emp_id)
        timesheet = self.env['hr.analytic.timesheet'].browse(timesheet_id)
        if data.task_id:
            timesheet.write({'task_id': data.task_id.id})
        return timesheet_id

    @api.onchange('task_id')
    def onchange_task(self):
        if self.task_id:
            self.info = "[%s]: " % self.task_id.name or ''
