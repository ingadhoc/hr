from datetime import date

from odoo import models


class HrLeaveAllocationGenerateMultiWizard(models.TransientModel):
    _inherit = "hr.leave.allocation.generate.multi.wizard"

    def action_generate_allocations(self):
        """Override to prevent auto-approval after batch creation.

        Upstream calls action_approve() right after create(), bypassing the
        validation flow configured on the leave type.  We reproduce the method
        without those calls so allocations land in 'confirm' (To Approve).
        no_validation types still auto-approve via the create() hook in
        hr.leave.allocation.
        """
        self.ensure_one()
        employees = self._get_employees_from_allocation_mode()
        vals_list = self._prepare_allocation_values(employees)
        if not vals_list:
            return None
        allocations = (
            self.env["hr.leave.allocation"]
            .with_context(
                mail_notify_force_send=False,
                mail_activity_automation_skip=True,
            )
            .create(vals_list)
        )
        accrual_allocations = allocations.filtered(lambda a: a.allocation_type == "accrual")
        for date_to, allocation in accrual_allocations.grouped("date_to").items():
            date_to = min(date_to, date.today()) if date_to else False
            allocation._process_accrual_plans(date_to)
        return {
            "type": "ir.actions.act_window",
            "name": self.env._("Generated Allocations"),
            "views": [
                [self.env.ref("hr_holidays.hr_leave_allocation_view_tree").id, "list"],
                [self.env.ref("hr_holidays.hr_leave_allocation_view_form_manager").id, "form"],
            ],
            "view_mode": "list",
            "res_model": "hr.leave.allocation",
            "domain": [("id", "in", allocations.ids)],
            "context": {"active_id": False},
        }
