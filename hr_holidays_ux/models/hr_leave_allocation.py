from odoo import _, models
from odoo.exceptions import UserError


class HrLeaveAllocation(models.Model):
    _inherit = "hr.leave.allocation"

    def action_reset_to_confirm(self):
        """Revert validated allocations back to 'To Approve' (confirm) state.

        Blocked when any selected allocation has leaves already taken, since
        reverting the approval would make those days go into deficit.
        Permission checks (officer/manager role) are enforced by
        _check_approval_update inside write().
        """
        blocked = self.filtered(lambda a: a.leaves_taken > 0)
        if blocked:
            raise UserError(
                _("The following allocations already have leaves taken and cannot be reset:\n%s")
                % "\n".join(blocked.mapped("display_name"))
            )
        self.filtered(lambda a: a.state in ("validate", "validate1")).write({"state": "confirm"})
