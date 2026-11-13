from lxml import html
from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestApplyPhoneMinlength(HttpCase):
    def test_apply_form_phone_minlength(self):
        job = self.env["hr.job"].create({"name": "Uxtest Phone Job", "is_published": True})

        response = self.url_open(f"/jobs/apply/{job.id}")

        self.assertEqual(response.status_code, 200)
        phone_inputs = html.fromstring(response.content).xpath("//input[@name='partner_phone']")
        self.assertEqual(len(phone_inputs), 1)
        self.assertEqual(phone_inputs[0].get("minlength"), "7")
