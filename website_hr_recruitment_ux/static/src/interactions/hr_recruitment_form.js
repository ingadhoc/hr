import { HrRecruitmentForm } from "@website_hr_recruitment/interactions/hr_recruitment_form";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

const MIN_PHONE_LENGTH = 7;

patch(HrRecruitmentForm.prototype, {
    setup() {
        super.setup();
        const phoneEl = this.el.querySelector("#recruitment3");
        if (phoneEl) {
            phoneEl.addEventListener("invalid", () => {
                if (phoneEl.validity.tooShort) {
                    phoneEl.setCustomValidity(_t("Please enter a valid phone number."));
                }
            });
            phoneEl.addEventListener("input", () => phoneEl.setCustomValidity(""));
            phoneEl.addEventListener("focusout", () => this.checkPhoneLength(phoneEl));
        }
    },

    checkPhoneLength(phoneEl) {
        if (!this.warningMessageEl) {
            return;
        }
        if (phoneEl.value && phoneEl.value.length < MIN_PHONE_LENGTH) {
            this.showWarningMessage(
                phoneEl,
                this.warningMessageEl,
                _t("Please enter a valid phone number.")
            );
        } else {
            this.hideWarningMessage(phoneEl, this.warningMessageEl);
        }
    },
});
