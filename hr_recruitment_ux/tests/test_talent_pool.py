# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form, TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestTalentPool(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pool_1, cls.pool_2 = cls.env["hr.talent.pool"].create([{"name": "Pool One"}, {"name": "Pool Two"}])
        cls.job = cls.env["hr.job"].create({"name": "Developer"})
        cls.applicant = cls.env["hr.applicant"].create({"partner_name": "Pool applicant", "job_id": cls.job.id})
        cls.cv = cls.env["ir.attachment"].create(
            {
                "name": "cv.pdf",
                "raw": b"cv",
                "res_model": "hr.applicant",
                "res_id": cls.applicant.id,
            }
        )

    def _add_to_pool(self, applicants, pools):
        wizard = Form(self.env["talent.pool.add.applicants"])
        wizard.applicant_ids = applicants
        wizard.talent_pool_ids = pools
        # Same entry point as the button, which runs with sudo
        wizard.save().action_add_applicants_to_pool()
        return applicants.pool_applicant_id

    def test_add_to_talent_pool_archives_original(self):
        """Only the applicant copied into a new talent is archived, and attachments are not duplicated."""
        with self.subTest("new applicant: the talent is created and the original archived with a note"):
            talent = self._add_to_pool(self.applicant, self.pool_1)
            self.assertNotEqual(talent, self.applicant)
            self.assertEqual(talent.talent_pool_ids, self.pool_1)
            self.assertFalse(self.applicant.active)
            self.assertTrue(talent.active)
            note = self.applicant.message_ids.filtered(lambda m: "Pool One" in (m.body or ""))
            self.assertEqual(len(note), 1)
            self.assertEqual(note.subtype_id, self.env.ref("mail.mt_note"))

        with self.subTest("attachments: the original keeps its own and the talent gets a single copy"):
            self.assertEqual(self.applicant.attachment_ids, self.cv)
            self.assertEqual(len(talent.attachment_ids), 1)
            self.assertNotEqual(talent.attachment_ids, self.cv)

        with self.subTest("applicant already linked to the talent: not archived, the talent gets the pool"):
            linked = self.env["hr.applicant"].create(
                {"partner_name": "Pool applicant", "job_id": self.job.id, "pool_applicant_id": talent.id}
            )
            result = self._add_to_pool(linked, self.pool_2)
            self.assertEqual(result, talent)
            self.assertTrue(linked.active)
            self.assertEqual(talent.talent_pool_ids, self.pool_1 | self.pool_2)
