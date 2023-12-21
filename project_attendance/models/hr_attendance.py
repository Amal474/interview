from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    pa_project_id = fields.Many2one(
        comodel_name='project.project', string='Project')
    pa_task_id = fields.Many2one(
        comodel_name='project.task', string='Task',
        domain="[('project_id', '=', pa_project_id)]")
    pa_description = fields.Char(string='Description')

    @api.constrains('pa_project_id', 'pa_task_id')
    def check_project_task_reln(self):
        for attendance_id in self:
            if attendance_id.pa_project_id.id or attendance_id.pa_task_id.id:
                if attendance_id.pa_task_id.project_id != attendance_id.pa_project_id:
                    raise ValidationError(_(
                        "Project should be related to task"))
