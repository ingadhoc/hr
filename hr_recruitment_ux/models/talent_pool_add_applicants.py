# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models


class TalentPoolAddApplicants(models.TransientModel):
    _inherit = "talent.pool.add.applicants"

    def _add_applicants_to_pool(self):
        # Capture originals before super creates copies in the pool
        originals_to_archive = self.applicant_ids.filtered(lambda a: not a.talent_pool_ids)
        for applicant in originals_to_archive:
            pool_names = ", ".join(self.talent_pool_ids.mapped("name"))
            applicant.message_post(
                body=_(
                    "Candidato derivado a Talent Pool: %(pools)s " "(vacante: %(job)s — etapa: %(stage)s)",
                    pools=pool_names,
                    job=applicant.job_id.name or _("sin vacante"),
                    stage=applicant.stage_id.name or _("sin etapa"),
                ),
                subtype_xmlid="mail.mt_note",
            )
        talents = super()._add_applicants_to_pool()
        for original in originals_to_archive:
            new_record = talents.filtered(lambda t: t.partner_id.id == original.partner_id.id)
            if not new_record:
                continue
            self.env["ir.attachment"].sudo().search(
                [
                    ("res_model", "=", "hr.applicant"),
                    ("res_id", "=", original.id),
                ]
            ).write({"res_id": new_record[0].id})
        originals_to_archive.write({"active": False})
        return talents
