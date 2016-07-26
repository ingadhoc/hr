# -*- coding: utf-8 -*-
from openerp import fields, models


class project(models.Model):
    _inherit = "project.project"

    timesheet_task_required = fields.Boolean(
        'Timesheet Task Required',
    )
