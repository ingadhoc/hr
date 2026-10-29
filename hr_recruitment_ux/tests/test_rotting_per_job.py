# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestRottingPerJob(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stage = cls.env["hr.recruitment.stage"].create(
            {
                "name": "Stage with per-job rotting",
                "rotting_threshold_days": 5,
                "use_rotting_per_job": True,
            }
        )
        cls.job_with_rule, cls.job_without_rule = cls.env["hr.job"].create(
            [{"name": "Job with own threshold"}, {"name": "Job without own threshold"}]
        )
        cls.job_rule = cls.env["hr.job.stage.rotting"].create(
            {"job_id": cls.job_with_rule.id, "stage_id": cls.stage.id, "rotting_days": 10}
        )

    def _applicant_in_stage_since(self, job, days):
        # Applicant that entered the stage `days` days ago
        applicant = self.env["hr.applicant"].create(
            {"partner_name": "Rotting applicant", "job_id": job.id, "stage_id": self.stage.id}
        )
        applicant.date_last_stage_update = self.env.cr.now() - timedelta(days=days)
        applicant.invalidate_recordset(["is_rotting", "rotting_days"])
        return applicant

    def _assert_rotting(self, applicant, expected_days):
        # Rotting flag and day count must agree
        self.assertTrue(applicant.is_rotting)
        self.assertEqual(applicant.rotting_days, expected_days)

    def _assert_not_rotting(self, applicant):
        self.assertFalse(applicant.is_rotting)
        self.assertEqual(applicant.rotting_days, 0)

    def test_job_threshold_overrides_stage_threshold(self):
        """The threshold of the job, when the stage enables it, replaces the one of the stage."""
        with self.subTest("job threshold not reached, stage threshold passed: not rotting"):
            self._assert_not_rotting(self._applicant_in_stage_since(self.job_with_rule, 7))

        with self.subTest("job threshold passed: rotting since the stage change"):
            self._assert_rotting(self._applicant_in_stage_since(self.job_with_rule, 12), 12)

        with self.subTest("job without its own threshold: the stage threshold applies"):
            self._assert_rotting(self._applicant_in_stage_since(self.job_without_rule, 7), 7)

        with self.subTest("per-job rotting disabled on the stage: the stage threshold applies"):
            self.stage.use_rotting_per_job = False
            self._assert_rotting(self._applicant_in_stage_since(self.job_with_rule, 7), 7)
            self.stage.use_rotting_per_job = True

        with self.subTest("job threshold set to 0: never rotting"):
            self.job_rule.rotting_days = 0
            self._assert_not_rotting(self._applicant_in_stage_since(self.job_with_rule, 30))
