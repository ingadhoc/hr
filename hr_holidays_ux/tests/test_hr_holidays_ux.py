from datetime import date

from odoo.addons.hr_holidays.tests.common import TestHrHolidaysCommon
from odoo.exceptions import UserError
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestHrHolidaysUx(TestHrHolidaysCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.no_alloc_type = cls.env["hr.work.entry.type"].create(
            {
                "name": "UX No Allocation",
                "code": "UXNA",
                "requires_allocation": False,
                "leave_validation_type": "hr",
                "request_unit": "day",
                "unit_of_measure": "day",
            }
        )
        cls.pre_approved_type = cls.env["hr.work.entry.type"].create(
            {
                "name": "UX Pre Approved",
                "code": "UXPA",
                "requires_allocation": False,
                "leave_validation_type": "hr",
                "support_document": True,
                "pre_approved_instance": True,
                "request_unit": "day",
                "unit_of_measure": "day",
            }
        )
        cls.alloc_type = cls.env["hr.work.entry.type"].create(
            {
                "name": "UX With Allocation",
                "code": "UXWA",
                "requires_allocation": True,
                "leave_validation_type": "hr",
                "allocation_validation_type": "manager",
                "request_unit": "day",
                "unit_of_measure": "day",
            }
        )

    def _create_leave(self, date_from, date_to, work_entry_type=None):
        # Created by the employee so it is not auto-approved on create
        leaves = (
            self.env["hr.leave"]
            .with_user(self.user_employee)
            .create(
                {
                    "employee_id": self.employee_emp.id,
                    "work_entry_type_id": (work_entry_type or self.no_alloc_type).id,
                    "request_date_from": date_from,
                    "request_date_to": date_to,
                }
            )
        )
        return leaves.with_env(self.env)

    def _employee_leaves(self):
        return self.env["hr.leave"].search([("employee_id", "=", self.employee_emp.id)], order="request_date_from")

    def test_create_splits_by_month(self):
        self._create_leave(date(2027, 1, 25), date(2027, 2, 3))
        self.assertEqual(
            [(leave.request_date_from, leave.request_date_to) for leave in self._employee_leaves()],
            [(date(2027, 1, 25), date(2027, 1, 31)), (date(2027, 2, 1), date(2027, 2, 3))],
        )

    def test_create_same_month_not_split(self):
        self._create_leave(date(2027, 1, 18), date(2027, 1, 22))
        self.assertEqual(len(self._employee_leaves()), 1)

    def test_write_splits_by_month(self):
        leave = self._create_leave(date(2027, 3, 1), date(2027, 3, 5))
        leave.write({"request_date_to": date(2027, 4, 2)})
        self.assertEqual(
            [(leave.request_date_from, leave.request_date_to) for leave in self._employee_leaves()],
            [(date(2027, 3, 1), date(2027, 3, 31)), (date(2027, 4, 1), date(2027, 4, 2))],
        )

    def test_write_split_skips_overlapping_period(self):
        leave = self._create_leave(date(2027, 3, 1), date(2027, 3, 5))
        existing = self._create_leave(date(2027, 4, 1), date(2027, 4, 2))
        leave.write({"request_date_to": date(2027, 4, 2)})
        self.assertEqual(self._employee_leaves(), leave | existing)
        self.assertEqual(leave.request_date_to, date(2027, 3, 31))

    def test_pre_approved_flow(self):
        leave = self._create_leave(date(2027, 3, 8), date(2027, 3, 9), self.pre_approved_type)
        leave.action_approve()
        self.assertEqual(leave.state, "pre-validate")
        self.env["ir.attachment"].create(
            {"name": "certificate.txt", "raw": b"doc", "res_model": "hr.leave", "res_id": leave.id}
        )
        leave.invalidate_recordset()
        self.assertTrue(leave.supported_attachment_ids)
        leave.action_post_approve()
        self.assertEqual(leave.state, "validate")

    def test_approve_without_pre_approved_instance(self):
        leave = self._create_leave(date(2027, 3, 8), date(2027, 3, 9))
        leave.action_approve()
        self.assertEqual(leave.state, "validate")

    def test_pre_validate_back_to_confirm_requires_officer(self):
        leave = self._create_leave(date(2027, 3, 8), date(2027, 3, 9), self.pre_approved_type)
        leave.action_approve()
        self.assertEqual(leave.state, "pre-validate")
        with self.assertRaisesRegex(UserError, "pre-validated"):
            leave.with_user(self.user_employee)._check_approval_update("confirm")

    def _create_allocation(self):
        allocation = self.env["hr.leave.allocation"].create(
            {
                "employee_id": self.employee_emp.id,
                "work_entry_type_id": self.alloc_type.id,
                "number_of_days": 10,
                "date_from": date(2027, 1, 1),
            }
        )
        allocation.action_approve()
        self.assertEqual(allocation.state, "validate")
        return allocation

    def test_reset_allocation_to_confirm(self):
        allocation = self._create_allocation()
        allocation.action_reset_to_confirm()
        self.assertEqual(allocation.state, "confirm")

    def test_reset_allocation_with_leaves_taken(self):
        allocation = self._create_allocation()
        self._create_leave(date(2027, 3, 8), date(2027, 3, 9), self.alloc_type).action_approve()
        allocation.invalidate_recordset()
        self.assertGreater(allocation.leaves_taken, 0)
        with self.assertRaisesRegex(UserError, "already have leaves taken"):
            allocation.action_reset_to_confirm()
        self.assertEqual(allocation.state, "validate")

    def test_generate_multi_allocations_not_approved(self):
        wizard = self.env["hr.leave.allocation.generate.multi.wizard"].create(
            {
                "work_entry_type_id": self.alloc_type.id,
                "employee_ids": [(6, 0, (self.employee_emp | self.employee_hruser).ids)],
                "duration": 5,
                "date_from": date(2027, 1, 1),
            }
        )
        action = wizard.action_generate_allocations()
        allocations = self.env["hr.leave.allocation"].search(action["domain"])
        self.assertEqual(len(allocations), 2)
        self.assertEqual(set(allocations.mapped("state")), {"confirm"})
