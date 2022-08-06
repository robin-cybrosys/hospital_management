from odoo import models, fields


# partners inherited from res.partner
class Employee(models.Model):
    _inherit = "hr.employee"

    company_id = fields.Many2one('res.company',
                                 string="Company",
                                 default=lambda self:
                                 self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency',
                                  related='company_id.currency_id',
                                  default=lambda self:
                                  self.env.user.company_id.currency_id.id)
    fee = fields.Monetary(store=True, string="Fee")
