from odoo import models, fields, _
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def attendance_manual_pa(
            self, pa_project_id, pa_task_id, pa_description, next_action):
        """
        Copied _attendance_action method to add project and task
        """
        self.ensure_one()
        employee = self.sudo()
        action_message = self.env["ir.actions.actions"]._for_xml_id("hr_attendance.hr_attendance_action_greeting_message")
        action_message['previous_attendance_change_date'] = employee.last_attendance_id and (employee.last_attendance_id.check_out or employee.last_attendance_id.check_in) or False
        action_message['employee_name'] = employee.name
        action_message['barcode'] = employee.barcode
        action_message['next_action'] = next_action
        action_message['hours_today'] = employee.hours_today
        action_message['kiosk_delay'] = employee.company_id.attendance_kiosk_delay * 1000

        if employee.user_id:
            modified_attendance = employee.with_user(employee.user_id).sudo()._attendance_action_change_pa(
                pa_project_id, pa_task_id, pa_description)
        else:
            modified_attendance = employee._attendance_action_change_pa(
                pa_project_id, pa_task_id, pa_description)
        action_message['attendance'] = modified_attendance.read()[0]
        action_message['total_overtime'] = employee.total_overtime

        action_message['overtime_today'] = self.env['hr.attendance.overtime'].sudo().search([
            ('employee_id', '=', employee.id), ('date', '=', fields.Date.context_today(self)), ('adjustment', '=', False)]).duration or 0
        return {'action': action_message}

    def _attendance_action_change_pa(self, pa_project_id, pa_task_id, pa_description):
        """
        Copied _attendance_action_change method to add project and task
        """
        self.ensure_one()
        action_date = fields.Datetime.now()

        if self.attendance_state != 'checked_in':
            vals = {
                'employee_id': self.id,
                'check_in': action_date,
                'pa_project_id': pa_project_id,
                'pa_task_id': pa_task_id,
                'pa_description': pa_description,
            }
            return self.env['hr.attendance'].create(vals)
        attendance = self.env['hr.attendance'].search([
            ('employee_id', '=', self.id),
            ('check_out', '=', False)], limit=1)
        if attendance:
            attendance.check_out = action_date
        else:
            raise ValidationError(_('Cannot perform check out on %(empl_name)s, could not find corresponding check in. '
                'Your attendances have probably been modified manually by human resources.') % {'empl_name': self.sudo().name, })
        return attendance
