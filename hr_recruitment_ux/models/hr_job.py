# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrJob(models.Model):
    _inherit = "hr.job"

    use_rotting_per_job = fields.Boolean(
        string="Usar días para deteriorarse por vacante",
        help="Cuando está activo, los días para deteriorarse se configuran a nivel de vacante "
        "en lugar de usar los días configurados en la etapa.",
    )
    rotting_threshold_days = fields.Integer(
        string="Días para deteriorarse",
        default=0,
        help="Cantidad de días antes de que los postulantes de esta vacante se deterioren. "
        "Se usa solo cuando 'Usar días para deteriorarse por vacante' está activo. "
        "0 = sin deterioro para esta vacante.",
    )
