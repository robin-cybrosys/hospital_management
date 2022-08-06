{
    'name': "Hospital Management",

    'application': "True",

    'sequence': "1",

    'summary': """Complete Hospital Management Package""",

    'author': "Cybrosys Technologies",

    'website': "http://www.cybrosys.com",

    'category': "Health Care",

    'version': '15.0.6.0.0',

    'licence': "LGPL-3",

    'depends': ['base', 'web', 'hr', 'account'],
    'assets': {
        'web.assets_backend': [
            "hospital_management/static/src/js/action_manager.js"]
    },

    'data': [
        'security/hospital_security_groups.xml',
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'report/hospital_op_history_templates.xml',
        'report/hospital_op_history_reports.xml',
        'report/hospital_reporting_wizard.xml',
        'views/hospital_res_partner.xml',
        'views/hospital_search_filters.xml',
        'views/hospital_hr_employee.xml',
        'views/hospital_form_views.xml',
        'views/hospital_views.xml',
        'views/hospital_op_views.xml',
        'views/hospital_consult_views.xml',
        'views/hospital_appointment_views.xml',
    ],
    'demo': [
        'demo/hospital_doctor_demo.xml',
        'demo/hr.department.csv',
        'demo/hr.job.csv',
        'demo/hr.employee.category.csv',
        'demo/hr.employee.csv'
    ],

}
