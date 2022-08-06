from datetime import datetime

from odoo import models, fields, api


# Appointment Model
class HospitalAppointment(models.Model):
    _name = "hospital.appointment"
    _rec_name = "token_no"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    patient_card_id = fields.Many2one(
        'hospital.management', required=True, string="Patient Card",
        help="Enter name of the Patient")
    patient_id = fields.Many2one(related='patient_card_id.patient_id',
                                 string='Patient',
                                 readonly=True)
    doctor_id = fields.Many2one(
        'hr.employee', domain="[('job_id', '=', 'Doctor')]", required=True)
    doctor_dept_id = fields.Many2one(
        related='doctor_id.department_id', readonly=True)
    date = fields.Date(default=datetime.today())
    token_no = fields.Char(string='Token',
                           readonly=True, default=lambda self: 'New',
                           copy=False)
    status = fields.Selection(
        [('draft_state', 'Draft'), ('appointment_state', 'Appointment'),
         ('op_state', 'OP')], default="draft_state", copy=False)
    active = fields.Boolean(default=True)
    appointment_op_count = fields.Integer(compute="compute_op_count")

    # confirm button
    def appointment_confirm_btn(self):
        for record in self:
            record.status = 'appointment_state'
        op_count = self.env['hospital.out_patient'].search_count([
            ('doctor_id', '=', self.doctor_id.id),
            ('date', '=', self.date),
            ('status', '=', 'confirm_state')])
        count = self.env['hospital.appointment'].search_count([
            ('doctor_id', '=', self.doctor_id.id),
            ('date', '=', self.date),
            ('status', '=', 'appointment_state')
        ])
        var = op_count + count
        self.write({'token_no': str('AP/00') + str(var)})
        return True

    # save:->draft
    @api.constrains('patient_card_id')
    def check_new(self):
        for tokens in self:
            if tokens.token_no == 'New':
                self.write({'token_no': "In Draft"})

    # convert_to_op button
    def compute_op_count(self):
        for res in self:
            no_of_op = self.env['hospital.out_patient'].search_count([
                ('patient_card_id', '=', self.patient_card_id.id)
            ])
            res.appointment_op_count = no_of_op

    # compute count for smart button
    def btn_to_op(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'OP Ticket',
            'view_mode': 'form',
            'res_model': 'hospital.out_patient',
            'domain': [('patient_id', '=', self.patient_id.name)],
            'target': 'new',
            'context': "{'default_patient_card_id': patient_card_id,"
                       "'default_doctor_id':doctor_id,"
                       "'default_token_no':token_no} "
        }

    def reset_draft_btn(self):
        for record in self:
            record.status = 'draft_state'

    def view_op_btn(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'OP Tickets',
            'view_type': 'tree',
            'view_mode': 'kanban,tree,form',
            'res_model': 'hospital.out_patient',
            'domain': [('patient_card_id', '=', self.patient_card_id.id)]
        }
