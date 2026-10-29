from datetime import datetime, time, timedelta

from odoo import fields
from odoo.addons.hr_timesheet.tests.test_timesheet import TestCommonTimesheet
from odoo.tests import Form, freeze_time, tagged
from odoo.tools.safe_eval import safe_eval


@tagged("post_install", "-at_install")
class TestHrTimesheetAttendanceUx(TestCommonTimesheet):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.today = fields.Date.today()
        # A past day, so a closed attendance never ends in the future.
        cls.day = cls.today - timedelta(days=1)

    def _new_timesheet_form(self, day):
        form = Form(
            # The suggestion cuts the day in the user's timezone: fix it.
            self.env["account.analytic.line"].with_user(self.user_employee).with_context(tz="UTC"),
            view="hr_timesheet.hr_timesheet_line_form",
        )
        form.project_id = self.project_customer
        form.date = day
        return form

    def test_suggested_hours_discount_break_and_logged_time(self):
        # The form runs in UTC, so these times stay inside the same day.
        self.env["hr.attendance"].create(
            {
                "employee_id": self.empl_employee.id,
                "check_in": datetime.combine(self.day, time(9)),
                "check_out": datetime.combine(self.day, time(17)),
                "break_duration": 0.5,
            }
        )
        self.env["account.analytic.line"].create(
            {
                "name": "Already logged",
                "project_id": self.project_customer.id,
                "employee_id": self.empl_employee.id,
                "date": self.day,
                "unit_amount": 2.0,
            }
        )
        form = self._new_timesheet_form(self.day)
        # 8 attended hours - 0.5 break - 2 already logged
        self.assertAlmostEqual(form.unit_amount, 5.5)
        line = form.save()
        self.assertEqual(line.employee_id, self.empl_employee)
        self.assertEqual(line.date, self.day)

        with self.subTest("open attendance counts up to now"):
            self.env["hr.attendance"].search([("employee_id", "=", self.empl_employee.id)]).unlink()
            with freeze_time(datetime.combine(self.today, time(15))):
                self.env["hr.attendance"].create(
                    {
                        "employee_id": self.empl_employee.id,
                        "check_in": datetime.combine(self.today, time(12)),
                    }
                )
                form = self._new_timesheet_form(self.today)
                self.assertAlmostEqual(form.unit_amount, 3.0)

    def test_task_domain_hides_folded_and_template_tasks(self):
        Task = self.env["project.task"]
        open_stage = self.env["project.task.type"].create({"name": "Open", "fold": False})
        folded_stage = self.env["project.task.type"].create({"name": "Done", "fold": True})
        self.project_customer.type_ids = [(6, 0, (open_stage | folded_stage).ids)]
        open_task = Task.create(
            {"name": "Open task", "project_id": self.project_customer.id, "stage_id": open_stage.id}
        )
        folded_task = Task.create(
            {"name": "Folded task", "project_id": self.project_customer.id, "stage_id": folded_stage.id}
        )
        template_task = Task.create(
            {
                "name": "Template task",
                "project_id": self.project_customer.id,
                "stage_id": open_stage.id,
                "is_template": True,
            }
        )
        domain = safe_eval(
            self.env["account.analytic.line"]._fields["task_id"].domain,
            {"company_id": self.project_customer.company_id.id, "project_id": self.project_customer.id},
        )
        available = Task.search(domain)
        self.assertIn(open_task, available)
        self.assertNotIn(folded_task, available)
        self.assertNotIn(template_task, available)
