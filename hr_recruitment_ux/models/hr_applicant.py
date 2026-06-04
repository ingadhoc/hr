# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import api, models


class HrApplicant(models.Model):
    _inherit = "hr.applicant"

    def _get_rotting_depends_fields(self):
        return super()._get_rotting_depends_fields() + [
            "stage_id.use_rotting_per_job",
            "stage_id.job_rotting_ids.job_id",
            "stage_id.job_rotting_ids.rotting_days",
        ]

    @api.depends(lambda self: self._get_rotting_depends_fields())
    def _compute_rotting(self):
        super()._compute_rotting()
        now = self.env.cr.now()
        candidates = self.filtered(
            lambda r: r.job_id and r.stage_id and r.application_status == "ongoing" and not r.date_closed
        )
        if not candidates:
            return
        overrides = self.env["hr.job.stage.rotting"].search_read(
            [
                ("job_id", "in", candidates.mapped("job_id").ids),
                ("stage_id.use_rotting_per_job", "=", True),
            ],
            ["job_id", "stage_id", "rotting_days"],
        )
        override_map = {(o["job_id"][0], o["stage_id"][0]): o["rotting_days"] for o in overrides}
        for applicant in candidates:
            key = (applicant.job_id.id, applicant.stage_id.id)
            if key not in override_map:
                continue
            threshold = override_map[key]
            date_ref = applicant.date_last_stage_update or applicant.create_date
            if threshold and date_ref and (date_ref + timedelta(days=threshold)) < now:
                applicant.is_rotting = True
                applicant.rotting_days = (now - date_ref).days
            else:
                applicant.is_rotting = False
                applicant.rotting_days = 0
