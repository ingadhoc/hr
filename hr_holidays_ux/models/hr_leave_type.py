from odoo import fields, models


class HrLeaveType(models.Model):
    _inherit = "hr.leave.type"

    pre_approved_instance = fields.Boolean(
        help="This instance is necessary when the supported document is added after the leave"
    )
