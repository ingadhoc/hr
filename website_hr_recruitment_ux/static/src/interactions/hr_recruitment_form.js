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
        }
    },

    async checkRedundant(targetEl, field, messageContainerEl, keepPreviousWarningMessage = false) {
        if (field === "phone" && targetEl.value && targetEl.value.length < MIN_PHONE_LENGTH) {
            this.showWarningMessage(
                targetEl,
                messageContainerEl,
                _t("Please enter a valid phone number.")
            );
            return;
        }
        return super.checkRedundant(targetEl, field, messageContainerEl, keepPreviousWarningMessage);
    },
});
