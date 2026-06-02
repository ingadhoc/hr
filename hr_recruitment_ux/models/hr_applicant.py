# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import api, models
from odoo.exceptions import UserError
from odoo.fields import Domain
from odoo.tools import SQL


class HrApplicant(models.Model):
    _inherit = "hr.applicant"

    def _get_rotting_depends_fields(self):
        return super()._get_rotting_depends_fields() + [
            "job_id.use_rotting_per_job",
            "job_id.rotting_threshold_days",
        ]

    def _get_rotting_domain(self):
        # Extend base domain to also include applicants with per-job rotting enabled.
        # Per-job applicants are included regardless of stage threshold.
        return super()._get_rotting_domain() | Domain(
            [
                ("job_id.use_rotting_per_job", "=", True),
                ("application_status", "=", "ongoing"),
                ("date_closed", "=", False),
            ]
        )

    def _is_rotting_feature_enabled(self):
        return super()._is_rotting_feature_enabled() or bool(
            not self or self.filtered(lambda r: r.job_id.use_rotting_per_job)
        )

    @api.depends(lambda self: self._get_rotting_depends_fields())
    def _compute_rotting(self):
        # super() handles stage-based rotting for all records.
        # Per-job applicants in 0-threshold stages are incorrectly set here;
        # the loop below corrects them.
        super()._compute_rotting()
        if not self._is_rotting_feature_enabled():
            return
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

    def _search_is_rotting(self, operator, value):
        if operator not in ["in", "not in"]:
            raise ValueError(self.env._('For performance reasons, use "=" operators on rotting fields.'))
        if not self._is_rotting_feature_enabled():
            raise UserError(self.env._("Model configuration does not support the rotting feature"))
        model_depends = [fname for fname in self._get_rotting_depends_fields() if "." not in fname]
        self.flush_model(model_depends)
        self.env[self[self._track_duration_field]._name].flush_model(["rotting_threshold_days"])
        self.env["hr.job"].flush_model(["use_rotting_per_job", "rotting_threshold_days"])
        base_query = self._search(self._get_rotting_domain())
        stage_table_alias_name = base_query.make_alias(self._table, self._track_duration_field)

        from_add_join = ""
        if not base_query._joins or stage_table_alias_name not in base_query._joins:
            from_add_join = """
                INNER JOIN %(stage_table)s AS %(stage_table_alias_name)s
                    ON %(stage_table_alias_name)s.id = %(table)s.%(stage_field)s
            """

        max_rotting_months = int(
            self.env["ir.config_parameter"].sudo().get_param("crm.lead.rot.max.months", default=12)
        )

        # effective_threshold logic:
        #   - use_rotting_per_job=True and threshold>0 → use job threshold
        #   - use_rotting_per_job=True and threshold=0  → NULLIF returns NULL → excluded (no rotting)
        #   - use_rotting_per_job=False                 → use stage threshold (standard behavior)
        query = f"""
            WITH perishables AS (
                SELECT  %(table)s.id AS id,
                        CASE WHEN hr_job.use_rotting_per_job
                            THEN NULLIF(hr_job.rotting_threshold_days, 0)
                            ELSE %(stage_table_alias_name)s.rotting_threshold_days
                        END AS effective_threshold,
                        %(table)s.date_last_stage_update
                FROM %(from_clause)s
                    {from_add_join}
                    LEFT JOIN hr_job ON hr_job.id = %(table)s.job_id
                WHERE
                    %(table)s.date_last_stage_update > %(today)s - INTERVAL '%(max_rotting_months)s months'
                    AND %(where_clause)s
            )
            SELECT id
            FROM perishables
            WHERE
                effective_threshold > 0
                AND %(today)s >= date_last_stage_update + effective_threshold * interval '1 day'
        """
        self.env.cr.execute(
            SQL(
                query,
                table=SQL.identifier(self._table),
                stage_table=SQL.identifier(self[self._track_duration_field]._table),
                stage_table_alias_name=SQL.identifier(stage_table_alias_name),
                stage_field=SQL.identifier(self._track_duration_field),
                today=self.env.cr.now(),
                where_clause=base_query.where_clause,
                from_clause=base_query.from_clause,
                max_rotting_months=max_rotting_months,
            )
        )
        rows = self.env.cr.dictfetchall()
        return [("id", operator, [r["id"] for r in rows])]
