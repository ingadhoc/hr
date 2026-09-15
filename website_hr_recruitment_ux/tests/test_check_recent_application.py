from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestCheckRecentApplication(HttpCase):
    def test_duplicate_warning_hides_recruiter_contact(self):
        recruiter = self.env["res.users"].create(
            {
                "name": "Zzrecruiter Uxtest",
                "login": "zzrecruiter_uxtest",
                "email": "zzrecruiter@example.com",
                "phone": "+54 341 000-0000",
            }
        )
        job = self.env["hr.job"].create({"name": "Uxtest Job", "is_published": True})
        self.env["hr.applicant"].create(
            {
                "job_id": job.id,
                "partner_name": "Uxtest Candidate",
                "partner_phone": "+54 341 111-1111",
                "user_id": recruiter.id,
            }
        )

        message = self.make_jsonrpc_request(
            "/website_hr_recruitment/check_recent_application",
            {"field": "phone", "value": "+54 341 111-1111", "job_id": job.id},
        )["message"]

        self.assertNotIn("zzrecruiter@example.com", message)
        self.assertNotIn("+54 341 000-0000", message)
        self.assertNotIn("Zzrecruiter Uxtest", message)
