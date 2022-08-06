from datetime import datetime

from odoo import models, fields, api


# op model
class OutPatient(models.Model):
    _name = "hospital.out_patient"
    _rec_name = "token_no"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    patient_card_id = fields.Many2one(
        'hospital.management', required=True, string="Patient Card",
        help="Enter name of the Patient")
    patient_id = fields.Many2one(
        related='patient_card_id.patient_id', readonly=False)
    age = fields.Char(related='patient_card_id.age', readonly=True)
    gender = fields.Selection(
        related='patient_card_id.gender', readonly=False)
    blood_group = fields.Selection(
        related='patient_card_id.blood_group', readonly=False)
    date = fields.Date(default=datetime.today())
    currency_id = fields.Many2one('res.currency',
                                  default=lambda self:
                                  self.env.user.company_id.currency_id.id)
    doctor_id = fields.Many2one(
        'hr.employee', domain="[('job_id', '=', 'Doctor')]", required=True,
        store=True)
    fee = fields.Monetary(default=lambda self: self.doctor_id.fee)
    doctor_dept_id = fields.Many2one(
        related='doctor_id.department_id', readonly=True, store=True)
    token_no = fields.Char(string='Token',
                           readonly=True, default=lambda self: 'New',
                           copy=False)
    active = fields.Boolean(default=True)
    status = fields.Selection(
        [('draft_state', 'Draft'), ('confirm_state', 'Confirmed'),
         ('paid_state', 'Paid')], default="draft_state", store=True, copy=False)

    invoice_no = fields.Char(string='Token',
                             readonly=True, default=lambda self: 'New',
                             copy=False, store=True)

    # op:confirm button-action
    def op_confirm_btn(self):
        # changing state to op
        for record in self:
            record.status = "confirm_state"
        # fetch:op count
        op_count = self.env['hospital.out_patient'].search_count([
            ('doctor_id', '=', self.doctor_id.id),
            ('date', '=', self.date),
            ('status', '=', 'confirm_state')])
        # fetch:app. count
        count = self.env['hospital.appointment'].search_count([
            ('doctor_id', '=', self.doctor_id.id),
            ('date', '=', self.date),
            ('status', '=', 'appointment_state')
        ])
        # change app. state,when: app->op
        rec = self.env['hospital.appointment'].search([
            ('status', '=', 'appointment_state'),
            ('patient_card_id', '=', self.patient_card_id.id)])
        rec.status = "op_state"
        # token_no:
        if rec.patient_card_id.id == self.patient_card_id.id:
            self.write({'token_no': str('OP/') + str(rec.token_no)})
        else:
            current_count = op_count + count
            self.write({'token_no': str('OP/') + str(current_count)})
        return True

    # save -> in draft
    @api.constrains('patient_card_id')
    def _check_New(self):
        for tokens in self:
            if tokens.token_no == 'New':
                self.write({'token_no': "In Draft"})

    # fee check
    @api.onchange('doctor_id')
    def _check_Fees(self):
        self.fee = self.doctor_id.fee

    # invoice
    def fee_btn(self):
        self.invoice_no = self.env['ir.sequence'].next_by_code(
            'hospital.invoice')
        move = self.env['account.move'].create([
            {
                'name': self.invoice_no,
                'move_type': 'out_invoice',
                'partner_id': self.patient_id.id,
                'date': self.date,
                # passing self(out_patient) to tokens(inside account.move )
                'tokens': self,
                'invoice_date': self.date,
                'invoice_line_ids': [(0, 0,
                                      {'name': 'Fee', 'price_unit': self.fee
                                       })],
            }, ])

        return {
            'view_type': 'form',
            'res_model': 'account.move',
            'res_id': move.id,
            'view_id': False,
            'view_mode': 'form',
            'type': 'ir.actions.act_window'

        }

    # def print_sample_report(self):
    #     data = {
    #         'model_id': self.id,
    #         'to_date': self.to_date,
    #         'from_date': self.from_date,
    #         'patient_id': self.patient_id.id,
    #         # 'vehicle_name': self.vehicle_id.vehicle_name
    #     }
    # docids = self.env['purchase.order'].search([]).ids
    # return self.env.ref(
    #     'hospital.out_patient.action_hospital_report_pdf').report_action(
    #     None, data=data)


# inheriting account.move and adding tokens (M2o-relation)
class AccountMove(models.Model):
    _inherit = 'account.move'
    tokens = fields.Many2one('hospital.out_patient')

    # fn when invoice is paid:
    @api.constrains('payment_state')
    def check_payment(self):
        for items in self:
            if items.payment_state == "paid":
                items.tokens.status = "paid_state"
