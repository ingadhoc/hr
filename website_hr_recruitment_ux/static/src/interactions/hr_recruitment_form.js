import { HrRecruitmentForm } from "@website_hr_recruitment/interactions/hr_recruitment_form";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

const MIN_PHONE_LENGTH = 7;

patch(HrRecruitmentForm.prototype, {
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
