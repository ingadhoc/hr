import calendar
from datetime import datetime, time, timedelta

from odoo import api, fields, models


class HrLeave(models.Model):
    _inherit = "hr.leave"

    state = fields.Selection(selection_add=[("pre-validate", "Pre-Approved")])

    def get_last_day_of_month(self, date):
        """Get last day of the month from the given date using monthrange."""
        last_day = calendar.monthrange(date.year, date.month)[1]
        return date.replace(day=last_day)

    def split_days(self, rec):
        """Split leave days across months."""
        new_records = []
        date_from = rec["request_date_from"]
        original_date_to = rec["request_date_to"]

        # ensure working with datetime objects
        date_from = self._convert_date_to_datetime(date_from)
        original_date_to = self._convert_date_to_datetime(original_date_to)

        while date_from <= original_date_to:
            # convert to date for get_last_day_of_month, then back to datetime
            date_from_date = self._convert_to_date(date_from)
            end_of_month_date = self.get_last_day_of_month(date_from_date)

            # convert back to datetime
            end_of_month = self._convert_date_to_datetime(end_of_month_date)

            if original_date_to <= end_of_month:
                # save the dates of the single record to be created
                new_records.append(
                    {
                        "request_date_from": date_from,
                        "request_date_to": original_date_to,
                    }
                )
                break
            else:
                # save the dates of each record to be created until reaching the end date of the leave, original_date_to
                new_records.append(
                    {
                        "request_date_from": date_from,
                        "request_date_to": end_of_month,
                    }
                )
                # Move to the first day of next month
                next_month_date = end_of_month_date + timedelta(days=1)
                date_from = self._convert_date_to_datetime(next_month_date)

        return new_records

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to automatically split leave records across months."""
        new_vals_list = []
        for vals in vals_list:
            date_from = vals.get("request_date_from")
            date_to = vals.get("request_date_to")

            # if the leave spans multiple months, split it into separate records
            if date_from and date_to and self._should_split_leave(date_from, date_to):
                # convert to datetime objects for split_days method
                date_from = self._convert_date_to_datetime(date_from)
                date_to = self._convert_date_to_datetime(date_to)
                split_records = self.split_days(
                    {
                        "request_date_from": date_from,
                        "request_date_to": date_to,
                    }
                )
                # create a separate record for each split period
                for rec in split_records:
                    new_vals = vals.copy()
                    new_vals.update(rec)
                    new_vals_list.append(new_vals)
            else:
                new_vals_list.append(vals)

        return super().create(new_vals_list)

    def _convert_date_to_datetime(self, date):
        """Convert string or date object to datetime object if needed."""
        if isinstance(date, str):
            return fields.Datetime.from_string(date)
        elif hasattr(date, "year") and not hasattr(date, "hour"):
            # date object: convert to datetime at start of day
            return datetime.combine(date, time.min)
        return date

    def _convert_to_date(self, date):
        """Convert datetime or string to date object for comparison."""
        if isinstance(date, str):
            return fields.Date.from_string(date)
        elif hasattr(date, "date"):
            # datetime object
            return date.date()
        return date

    def _should_split_leave(self, date_from, date_to):
        """Check if leave period needs to be split across months."""
        # convert to date objects for month comparison
        date_from = self._convert_to_date(date_from)
        date_to = self._convert_to_date(date_to)
        last_day_of_month = self.get_last_day_of_month(date_from)
        return date_to > last_day_of_month

    def _check_overlapping_leaves(self, record, date_from, date_to):
        """Check if there are existing leave records that overlap with the given dates."""
        domain = [
            ("employee_id", "=", record.employee_id.id),
            ("id", "!=", record.id),  # Exclude current record being edited
            ("state", "not in", ["cancel", "refuse"]),  # Only active leaves
            # Check for date overlap: (start1 <= end2) and (end1 >= start2)
            ("request_date_from", "<=", date_to),
            ("request_date_to", ">=", date_from),
        ]
        return self.search(domain)

    def write(self, vals):
        """Override write to handle automatic splitting when dates are modified."""
        date_from = vals.get("request_date_from")
        date_to = vals.get("request_date_to")

        # if no date fields are being modified, proceed with normal write
        if not (date_from or date_to):
            return super().write(vals)

        # for each record, check if it needs splitting after the write
        for record in self:
            # get the final dates. New values override existing ones
            final_date_from = date_from or record.request_date_from
            final_date_to = date_to or record.request_date_to

            # check if this record needs to be split
            if self._should_split_leave(final_date_from, final_date_to):
                # convert dates for split_days method (needs datetime objects)
                final_date_from = self._convert_date_to_datetime(final_date_from)
                final_date_to = self._convert_date_to_datetime(final_date_to)

                # get split records
                split_records = self.split_days(
                    {
                        "request_date_from": final_date_from,
                        "request_date_to": final_date_to,
                    }
                )

                # only split if we actually get multiple records
                if len(split_records) > 1:
                    # prepare values for the first record (update current record)
                    first_split = split_records[0]
                    first_vals = vals.copy()
                    first_vals.update(first_split)

                    # update current record with first split period
                    super(HrLeave, record).write(first_vals)

                    # check for overlapping records before creating new ones
                    records_to_create = []
                    for split_rec in split_records[1:]:
                        split_date_from = self._convert_to_date(split_rec["request_date_from"])
                        split_date_to = self._convert_to_date(split_rec["request_date_to"])

                        # check if there are overlapping records for this period
                        overlapping = self._check_overlapping_leaves(record, split_date_from, split_date_to)

                        if not overlapping:
                            # no overlapping records, safe to create
                            base_vals = {
                                "employee_id": record.employee_id.id,
                                "holiday_status_id": record.holiday_status_id.id,
                            }

                            # add fields that exist in vals or record, safely
                            safe_fields = [
                                "number_of_days",
                                "state",
                                "notes",
                                "date_from",
                                "date_to",
                                "name",
                                "description",
                                "request_unit_half",
                                "request_unit_hours",
                            ]

                            for field in safe_fields:
                                if field in vals:
                                    base_vals[field] = vals[field]
                                elif hasattr(record, field):
                                    base_vals[field] = getattr(record, field, False)

                            # add any other vals being updated (except date fields that will be overridden)
                            for key, value in vals.items():
                                if key not in ["request_date_from", "request_date_to"]:
                                    base_vals[key] = value

                            new_vals = base_vals.copy()
                            new_vals.update(split_rec)
                            records_to_create.append(new_vals)
                        # if overlapping records exist, skip creating this split
                        # this allows editing the current record but prevents duplicates

                    # create only the non-overlapping records
                    if records_to_create:
                        self.create(records_to_create)
                else:
                    super(HrLeave, record).write(vals)
            else:
                super(HrLeave, record).write(vals)

        return True

    def copy_data(self, default=None):
        """Override copy_data to handle leave splitting properly."""
        return super().copy_data(default=default)

    def action_approve(self, check_state=True):
        res = super().action_approve()
        if (
            self.state == "validate"
            and not self.supported_attachment_ids
            and self.holiday_status_id.pre_approved_instance
        ):
            self.state = "pre-validate"
        return res

    def action_validate(self, check_state=True):
        res = super().action_validate()
        if not self.supported_attachment_ids and self.holiday_status_id.pre_approved_instance:
            self.state = "pre-validate"
        return res

    def action_post_approve(self):
        """Approve a pre-validated leave once documents are uploaded."""
        self.write({"state": "validate"})
        self._validate_leave_request()
        if not self.env.context.get("leave_fast_create"):
            self.activity_update()
        return True

    def _get_next_states_by_state(self):
        """Override to add pre-validate state transitions."""
        state_result = super()._get_next_states_by_state()

        # Add pre-validate state to the state_result dictionary
        state_result["pre-validate"] = set()

        is_officer = self.env.user.has_group("hr_holidays.group_hr_holidays_user")
        is_time_off_manager = self.employee_id.leave_manager_id == self.env.user

        if is_officer or is_time_off_manager:
            # From pre-validate, you can go to validate, refuse, or cancel
            state_result["pre-validate"].update({"validate", "refuse", "cancel"})

        return state_result

    def _check_approval_update(self, state, raise_if_not_possible=True):
        """Override to handle pre-validate state transitions."""
        # For transitions from pre-validate state
        if self.state == "pre-validate" and state == "validate":
            # Allow transition from pre-validate to validate
            is_officer = self.env.user.has_group("hr_holidays.group_hr_holidays_user")
            is_time_off_manager = self.employee_id.leave_manager_id == self.env.user

            if is_officer or is_time_off_manager:
                return True

            if raise_if_not_possible:
                from odoo.exceptions import UserError

                raise UserError(self.env._("Only a Time Off Officer/Manager can approve a pre-validated leave."))
            return False

        return super()._check_approval_update(state, raise_if_not_possible)
