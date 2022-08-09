from datetime import datetime
from odoo import models, fields, api


# consultation model
class HospitalConsultation(models.Model):
    _name = "hospital.consultation"
    _rec_name = "patient_id"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    patient_card_id = fields.Many2one(
        'hospital.management', required=True, string="Patient Card",
        help="Enter name of the Patient")
    patient_id = fields.Many2one(
        related='patient_card_id.patient_id', string='Token', readonly=True,
        copy=False, store=True)
    consultation_type = fields.Selection(
        [('type_op', 'Out Patient(OP)'), ('type_ip', 'In Patient(IP)')],
        default="type_op")
    doctor_id = fields.Many2one(
        'hr.employee', domain="[('job_id', '=', 'Doctor')]", required=True,
    )
    doctor_dept_id = fields.Many2one(
        related='doctor_id.department_id', readonly=True, store=True)
    date = fields.Date(default=datetime.today())
    consultation_id = fields.Char(string='Token',
                                  readonly=True, default='New',
                                  copy=False)
    disease_id = fields.Many2one('hospital.disease', required=True)
    medicine_id = fields.Many2one(
        'hospital.treatment')
    diagnosis = fields.Html(string="Diagnosis"
                            )
    treatment_ids = fields.One2many(
        'hospital.treatment', 'consult_id', string="Treatment", store=True)
    status = fields.Selection(
        [('draft_state', 'Draft'), ('confirm_state', 'Confirmed')],
        default="draft_state", copy=False)
    active = fields.Boolean(default=True)

    def consult_btn(self):
        for record in self:
            record.status = 'confirm_state'
        self.consultation_id = self.env['ir.sequence'].next_by_code(
            'hospital.consult')

    @api.constrains('patient_card_id')
    def _check_New(self):
        for tokens in self:
            if tokens.consultation_id == 'New':
                self.write({'consultation_id': "In Draft"})

