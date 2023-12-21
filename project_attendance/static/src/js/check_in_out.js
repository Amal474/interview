/** @odoo-module **/

import MyAttendances from 'hr_attendance.my_attendances';

const session = require('web.session');
const { useState } = owl;


MyAttendances.include({

    willStart: function () {
        var self = this;

        var def = this._rpc({
            model: 'project.project',
            method: 'search_read',
            args: [[['active', '=', true]], ['id', 'name']],
        })
        .then(function (res) {
            self.project_ids = res.length ? res : []
        });

        this._rpc({
            model: 'project.task',
            method: 'search_read',
            args: [[['active', '=', true]], ['id', 'name', 'project_id']],
        })
        .then(function (result) {
            self.task_ids = result.length ? result : []
        });
        return Promise.all([def, this._super.apply(this, arguments)]);
    },

    update_attendance: function () {
        var self = this;

        if (this.employee.attendance_state!='checked_in') {
          var pa_project_id = parseInt(document.getElementById("attendance_project").value);
          var pa_task_id = parseInt(document.getElementById("attendance_task").value);
          var pa_description = document.getElementById("description").value;

          this._rpc({
                  model: 'hr.employee',
                  method: 'attendance_manual_pa',
                  args: [[self.employee.id], pa_project_id, pa_task_id, pa_description, 'hr_attendance.hr_attendance_action_my_attendances'],
                  context: session.user_context,
              })
              .then(function(result) {
                  if (result.action) {
                      self.do_action(result.action);
                  } else if (result.warning) {
                      self.displayNotification({ title: result.warning, type: 'danger' });
                  }
              });
        } else {
          this._rpc({
                  model: 'hr.employee',
                  method: 'attendance_manual',
                  args: [[self.employee.id], 'hr_attendance.hr_attendance_action_my_attendances'],
                  context: session.user_context,
              })
              .then(function(result) {
                  if (result.action) {
                      self.do_action(result.action);
                  } else if (result.warning) {
                      self.displayNotification({ title: result.warning, type: 'danger' });
                  }
              });
        }
    },

});
