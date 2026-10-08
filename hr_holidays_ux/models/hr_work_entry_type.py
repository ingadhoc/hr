from odoo import fields, models


class HrWorkEntryType(models.Model):
    _inherit = "hr.work.entry.type"

    pre_approved_instance = fields.Boolean(
        help="This instance is necessary when the supported document is added after the leave"
    )
