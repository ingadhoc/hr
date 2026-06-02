# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import api, models


class HrApplicant(models.Model):
    _inherit = "hr.applicant"

    def _get_rotting_depends_fields(self):
        return super()._get_rotting_depends_fields() + [
            "job_id.use_rotting_per_job",
            "job_id.rotting_threshold_days",
        ]

    @api.depends(lambda self: self._get_rotting_depends_fields())
    def _compute_rotting(self):
        super()._compute_rotting()
        now = self.env.cr.now()
        per_job = self.filtered(
            lambda r: r.job_id.use_rotting_per_job and r.application_status == "ongoing" and not r.date_closed
        )
        for applicant in per_job:
            threshold = applicant.job_id.rotting_threshold_days
            date_ref = applicant.date_last_stage_update or applicant.create_date
            if threshold and date_ref and (date_ref + timedelta(days=threshold)) < now:
                applicant.is_rotting = True
                applicant.rotting_days = (now - date_ref).days
            else:
                applicant.is_rotting = False
                applicant.rotting_days = 0
