# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrJobStageRotting(models.Model):
    _name = "hr.job.stage.rotting"
    _description = "Días para deteriorarse por vacante y etapa"

    job_id = fields.Many2one("hr.job", required=True, ondelete="cascade")
    stage_id = fields.Many2one("hr.recruitment.stage", required=True)
    rotting_days = fields.Integer(
        string="Días para deteriorarse",
        default=0,
        help="0 = sin deterioro para esta combinación de vacante y etapa.",
    )

    _unique_job_stage = models.Constraint(
        "UNIQUE(job_id, stage_id)",
        "Ya existe una configuración para esta vacante y etapa.",
    )
