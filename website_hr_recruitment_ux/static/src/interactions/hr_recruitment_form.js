import { HrRecruitmentForm } from "@website_hr_recruitment/interactions/hr_recruitment_form";
import { patch } from "@web/core/utils/patch";

const MIN_PHONE_LENGTH = 7;

patch(HrRecruitmentForm.prototype, {
    async checkRedundant(targetEl, field, messageContainerEl, keepPreviousWarningMessage = false) {
        if (field === "phone" && targetEl.value && targetEl.value.length < MIN_PHONE_LENGTH) {
            this.hideWarningMessage(targetEl, messageContainerEl);
            return;
        }
        return super.checkRedundant(targetEl, field, messageContainerEl, keepPreviousWarningMessage);
    },
});
