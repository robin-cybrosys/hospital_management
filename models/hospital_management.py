from datetime import date

from odoo import models, fields, api

# patient card
from odoo.exceptions import ValidationError


class HospitalManagement(models.Model):
    _name = 'hospital.management'
    _rec_name = 'reference_no'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    reference_no = fields.Char(string='Patient ID',
                               readonly=True, default=lambda self: 'New',
                               copy=False)
    patient_id = fields.Many2one(
        'res.partner', required=True, help="Enter name of the Patient")
    image = fields.Image(related='patient_id.image_1920')
    patient_phone = fields.Char(related='patient_id.phone', readonly=False)
    patient_mobile = fields.Char(related='patient_id.mobile', readonly=False)
    street = fields.Char(related='patient_id.street', readonly=False)
    street2 = fields.Char(related='patient_id.street2', readonly=False)
    zip = fields.Char(related='patient_id.zip', readonly=False)
    city = fields.Char(related='patient_id.city', readonly=False)
    state_id = fields.Many2one(related='patient_id.state_id', readonly=False)
    country_id = fields.Many2one(related='patient_id.country_id',
                                 readonly=False)
    gender = fields.Selection(
        related="patient_id.gender", readonly=False)
    blood_group = fields.Selection(
        related="patient_id.blood_group", readonly=False, store=True)
    dob = fields.Date(copy=False, readonly=False)
    age = fields.Char(compute="_compute_age", readonly=True,
                      tracking=True)
    active = fields.Boolean(default=True)
    op_ids = fields.One2many(
        'hospital.out_patient', 'patient_card_id', string="OP-Tickets")

    # age computation
    @api.depends('dob')
    def _compute_age(self):
        for rec in self:
            today = date.today()
            if not rec.dob:
                rec.age = None
            else:
                year = rec.dob.year
                month = rec.dob.month
                day = rec.dob.day
                if year == today.year:
                    if month == today.month:
                        rec.age = str(today.day - day) + " Days"
                    if month != today.month:
                        rec.age = str(
                            today.month - month) + " Months "
                    if month >= today.month and day > today.day:
                        raise ValidationError(
                            "Enter a valid Date of birth")
                if year != today.year:
                    if year > today.year:
                        raise ValidationError(
                            "Enter a valid Year of birth")
                    else:
                        rec.age = str(today.year - year) + " Years"

    # sequence -creation
    @api.model
    def create(self, vals):
        vals['reference_no'] = self.env['ir.sequence'].next_by_code(
            'hospital.patient')
        res = super(HospitalManagement, self).create(vals)
        return res
