# -*- coding: utf-8 -*-
{
    'name': 'Project Task in Attendance',
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'license': 'OPL-1',
    'summary': """
        Select project and task while marking attendance
    """,
    'depends': [
        'base',
        'project',
        'hr_attendance',
    ],
    'author': 'Mohammed Amal N',
    'description': """ Updates Below
    """,
    'data': [
        'views/hr_attendance_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'project_attendance/static/src/js/check_in_out.js',
            'project_attendance/static/src/xml/check_in_out.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
