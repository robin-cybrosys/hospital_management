from odoo import models, fields


# Disease Model
class HospitalDisease(models.Model):
    _name = 'hospital.disease'
    _description = 'hospital.disease'
    _rec_name = "disease"

    disease = fields.Char(string="Disease")
    disease_ref_no = fields.Char(string='Disease ID')
    Symptoms = fields.Html(string="Symptoms")
    description = fields.Html(string="Description")


# Medicine Model
class HospitalMedicine(models.Model):
    _name = "hospital.medicine"
    _rec_name = "medicine"

    medicine = fields.Char(string="Medicine")
    dosage = fields.Char(string="Dosage")
    days = fields.Char(string="Days")
    description = fields.Text(string="Description")
    # treatment_id = fields.Many2one('hospital.consultation')


# Treatment Model
class HospitalTreatment(models.Model):
    _name = "hospital.treatment"
    _rec_name = "medicine_id"

    medicine_id = fields.Many2one('hospital.medicine', required=True)
    dosage = fields.Char(string="Dosage")
    days = fields.Char(string="Days")
    description = fields.Text(string="Description")
    consult_id = fields.Many2one('hospital.consultation')
