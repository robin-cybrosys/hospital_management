import datetime
import io
import json
import time

from odoo import fields, models
from odoo.exceptions import ValidationError
from odoo.tools import date_utils
from odoo import models, fields

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


# wizard for printing reports
class HospitalReporting(models.TransientModel):
    _name = "hospital.report.wizard"

    # fields for filtering
    to_date = fields.Date()
    from_date = fields.Date()
    patient_id = fields.Many2one(
        'hospital.management', readonly=False)
    sequence_id = fields.Char(related='patient_id.reference_no')
    doctor_id = fields.Many2one(
        'hr.employee', domain="[('job_id', '=', 'Doctor')]",
        store=True)
    disease_id = fields.Many2one('hospital.disease')
    dept_id = fields.Many2one(
        'hr.department', store=True)

    def report_filters(self):
        dto = self.to_date
        dfrom = self.from_date
        patient = self.patient_id.patient_id.id
        doctor = self.doctor_id.id
        disease = self.disease_id.id
        dept = self.dept_id.id

        # main query for fetching all required results
        query = """ Select t1.name as p_name,t2.date,t3.name as doc_name,t4.name as dep_name,t5.disease,t6.token_no
            from res_partner t1 
            inner join hospital_consultation t2 
            on t1.id = t2.patient_id
            inner join hr_employee t3 on t3.id=t2.doctor_id
            inner join hr_department t4 on t4.id=t2.doctor_dept_id
            inner join hospital_disease t5 on t5.id=t2.disease_id
            inner join hospital_out_patient t6 on t6.id=t2.patient_card_id
            """
        where = "where "
        # setting flag for checking&applying where condition
        flag = 0
        # condition1: if no filter is used
        if not {patient} and not {doctor} and not {dept} and not {disease}:
            query = """{}""".format(query)

        # condition2: if->only patient; else->appending patient to other condn
        if self.patient_id:
            if flag == 0:
                flag = 1
                query = """{} {} t2.patient_id = {}""".format(
                    query, where, patient
                )
            else:
                query = """{} and t2.patient_id = {}""".format(
                    query, patient)
        # condition3: if->only doc; else->appending doc
        if self.doctor_id:
            if flag == 0:
                flag = 1
                query = """{} {} t2.doctor_id = {}""".format(
                    query, where, doctor
                )
            else:
                query = """{} and t2.doctor_id = {}""".format(
                    query, doctor)
        # condition4: if->only dept; else->appending dept
        if self.dept_id:
            if flag == 0:
                flag = 1
                query = """{} {} t2.doctor_dept_id = {}""".format(
                    query, where, dept
                )
            else:
                query = """{} and t2.doctor_dept_id = {}""".format(
                    query, dept)
        # condition5: if->only disease; else->appending disease
        if self.disease_id:
            if flag == 0:
                flag = 1
                query = """{} {} t2.disease_id = {}""".format(
                    query, where, disease
                )
            else:
                query = """{} and t2.disease_id = {}""".format(
                    query, disease)
        # condition6: if->only to date; else->appending to date
        if self.to_date:
            if flag == 0:
                flag = flag + 1
                query = """{} {} t2.date<='{}'""".format(
                    query, where, dto)
            else:
                query = """{} and t2.date<='{}'""".format(
                    query, dto)
        # condition7: if->only from date; else->appending from date
        if self.from_date:
            if flag == 0:
                flag = flag + 1
                query = """{} {} t2.date>='{}'""".format(
                    query, where, dfrom)
            else:
                query = """{} and t2.date>='{}'""".format(
                    query, dfrom)
        self.env.cr.execute(query)
        res = self.env.cr.dictfetchall()
        return res

    # pdf ()
    def print_pdf_report(self):
        res = self.report_filters()
        # executing query and returns data{} to report->template
        data = {
            'to_date': self.to_date,
            'from_date': self.from_date,
            'sequence_id': self.sequence_id,
            'patient_id': self.patient_id.patient_id.name,
            'doctor_id': self.doctor_id.name,
            'disease_id': self.disease_id.disease,
            'dept_id': self.dept_id.name,
            'res': res
        }

        # print( res)
        return self.env.ref(
            'hospital_management.action_report_out_patient_pdf'
        ).report_action(None, data=data)

    # xls()
    def print_xls_report(self):
        # pass
        # if self.from_date >= self.to_date:
        #     raise ValidationError('From Date must be less than To Date')
        res = self.report_filters()

        data = {
            'to_date': self.to_date,
            'from_date': self.from_date,
            'sequence_id': self.sequence_id,
            'patient_id': self.patient_id.patient_id.name,
            'doctor_id': self.doctor_id.name,
            'disease_id': self.disease_id.disease,
            'dept_id': self.dept_id.name,
            'res': res
        }
        # print(data, "ssdsss")
        # print(data, "print_xlsx")
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'hospital.report.wizard',
                     'output_format': 'xlsx',
                     'options': json.dumps(
                         data, default=date_utils.json_default),
                     'report_name': 'Excel Report',
                     },
            'report_type': 'xlsx'
        }

    def get_xlsx_report(self, data, response):
        print("---data", data, "data----")
        # print("---res", data['res'], "res---")
        # for o in data:
        #     if not data['']:
        #         print(o['doc_name'])
        # for o in data['res']:
        #     print(o['token_no'])
        #     print(o['p_name'])
        #     print(o['date'])
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        head = workbook.add_format(
            {'align': 'center', 'bold': True, 'bg_color': '#009688',
             'font_color': '#FFFFFF',
             'font_size': '20px'})
        detail_format = workbook.add_format(
            {'font_size': '11px','bg_color': '#e3e3e3','font_color': '#2f4f4f', 'align': 'left',
             'bold': True})
        # 'bg_color': '#D3D3D3',
        data_format = workbook.add_format(
            {'align': 'left', 'bold': True, 'font_size': '11px'})
        title_format = workbook.add_format(
            {'font_size': '11px', 'bg_color': '#d9dde1',
             'font_color': '#2f4f4f', 'align': 'center',
             'bold': True})
        txt = workbook.add_format({'align': 'center', 'font_size': '11px'})
        worksheet.set_column(1, 13, 15)
        worksheet.merge_range('B2:H3', 'Medical Report', head)
        if data['patient_id']:
            worksheet.write('B5', 'Patient:', detail_format)
            worksheet.merge_range('C5:D5', data['sequence_id'], data_format)
            worksheet.merge_range('C6:D6', data['patient_id'], data_format)
        if data['from_date']:
            worksheet.write('B7', 'From Date:', detail_format)
            worksheet.merge_range('C7:D7', data['from_date'], data_format)
        if data['to_date']:
            worksheet.write('B8', 'To Date:', detail_format)
            worksheet.merge_range('C8:D8', data['to_date'], data_format)
        if data['doctor_id']:
            worksheet.write('F5', 'Doctor:', detail_format)
            worksheet.merge_range('G5:H5', data['doctor_id'], data_format)
        if data['disease_id']:
            worksheet.write('F6', 'Disease:', detail_format)
            worksheet.merge_range('G6:H6', data['disease_id'], data_format)
        if data['dept_id']:
            worksheet.write('F7', 'Department:', detail_format)
            worksheet.merge_range('G7:H7', data['dept_id'], data_format)



        worksheet.write('B10', 'SL.No', title_format)
        worksheet.write('C10', 'OP', title_format)
        worksheet.write('D10', 'Patient', title_format)
        worksheet.write('E10', 'Date', title_format)
        worksheet.write('F10', 'Doctor', title_format)
        worksheet.write('G10', 'Department', title_format)
        worksheet.write('H10', 'Disease', title_format)
        row = 11
        col = 1
        seq = 1
        for o in data['res']:
            worksheet.write(row, col, seq, txt)
            worksheet.write(row, col + 1, o['token_no'], txt)
            worksheet.write(row, col + 2, o['p_name'], txt)
            worksheet.write(row, col + 3, o['date'], txt)
            worksheet.write(row, col + 4, o['doc_name'], txt)
            worksheet.write(row, col + 5, o['dep_name'], txt)
            worksheet.write(row, col + 6, o['disease'], txt)

            row += 1
            seq += 1

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
