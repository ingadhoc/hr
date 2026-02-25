# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class TalentPoolAddApplicants(models.TransientModel):
    _inherit = "talent.pool.add.applicants"

    def action_add_applicants_to_pool(self):
        result = super().action_add_applicants_to_pool()
        # Archive the original applicants after adding them to the talent pool
        self.applicant_ids.write({"active": False})
        return result
