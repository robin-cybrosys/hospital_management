from odoo import models, fields


# inherited from res.partner
class ResPatient(models.Model):
    _inherit = "res.partner"

    gender = fields.Selection(
        [('male', 'Male'), ('female', 'Female'), ('others', 'Others')])

    blood_group = fields.Selection([
        ('a_positive', 'A +ve'), ('a_negative', 'A -ve'),
        ('b_positive', 'B +ve'), ('b_negative', 'B -ve'),
        ('ab_positive', 'AB +ve'), ('ab_negative', 'AB -ve'),
        ('o_positive', 'O +ve'), ('o_negative', 'O -ve')], string="Blood Group")

    dob = fields.Date(copy=False, string="D.O.B")
