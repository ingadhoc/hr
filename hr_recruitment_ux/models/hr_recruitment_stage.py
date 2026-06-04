# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrRecruitmentStage(models.Model):
    _inherit = "hr.recruitment.stage"

    use_rotting_per_job = fields.Boolean(
        string="¿Días para deteriorarse por posición?",
    )
    job_rotting_ids = fields.One2many(
        "hr.job.stage.rotting",
        "stage_id",
        string="Días para deteriorarse por posición",
    )
