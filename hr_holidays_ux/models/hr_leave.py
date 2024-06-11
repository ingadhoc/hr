from odoo import api, fields, models, _
from datetime import timedelta
import calendar

class HrLeave(models.Model):
    _inherit = 'hr.leave'

    def get_last_day_of_month(self, date):
        """Get last day of the month from the given date using monthrange."""
        last_day = calendar.monthrange(date.year, date.month)[1]
        return date.replace(day=last_day)

    def split_days(self, rec):
        """Split leave days across months."""
        new_records = []
        date_from = rec['request_date_from']
        original_date_to = rec['request_date_to']

        while date_from <= original_date_to:
            # get last day of the month
            end_of_month = self.get_last_day_of_month(date_from)
            if original_date_to <= end_of_month:
                # save the dates of the single record to be created
                new_records.append({
                    'request_date_from': date_from,
                    'request_date_to': original_date_to,
                })
                break
            else:
                # save the dates of each record to be created until reaching the end date of the leave, original_date_to
                new_records.append({ 
                    'request_date_from': date_from,
                    'request_date_to': end_of_month,
                })
                date_from = end_of_month + timedelta(days=1)

        return new_records

    
    @api.model_create_multi
    def create(self, vals_list):
        new_vals_list = []
        for vals in vals_list:
            date_from = vals.get('request_date_from')
            date_to = vals.get('request_date_to')

            if date_from and date_to:
                # convert to datetime objects if they are strings
                if isinstance(date_from, str):
                    date_from = fields.Datetime.from_string(date_from)
                if isinstance(date_to, str):
                    date_to = fields.Datetime.from_string(date_to)                
            
            # if the leave ends in a different month, call the split_days() method to get the dates for splitting the leaves
            if date_to > self.get_last_day_of_month(date_from):
                split_records = self.split_days({
                    'request_date_from' : date_from,
                    'request_date_to' : date_to,
                })
                # for each record generated in split_days, copy the original vals, and update with the dates of the record rec, adding them to a new list
                for rec in split_records:
                    new_vals = vals.copy()
                    new_vals.update(rec)
                    new_vals_list.append(new_vals)
            else:
                new_vals_list.append(vals)

        return super().create(new_vals_list)
    
