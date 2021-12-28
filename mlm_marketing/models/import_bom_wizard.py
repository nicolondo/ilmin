# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models, _
from datetime import datetime
from odoo.exceptions import UserError
import csv
import base64
import xlrd
from odoo.tools import ustr
import logging


_logger = logging.getLogger(__name__)


class ImportBSLWizard(models.TransientModel):
    _name = "mlm_marketing.bom.wizard"
    _description = "Import Bom Wizard"

    file = fields.Binary(string="File", required=True)

    def import_bom_apply(self):

        absl_obj = self.env['account.bank.statement.line']
        ir_model_fields_obj = self.env['ir.model.fields']

        #perform import lead
        if self and self.file and self.env.context.get("sh_abs_id", False):
            #For CSV
            if self.import_type == 'csv':
                for rec in self:
                    counter = 0
                    try:
                        file = str(base64.decodebytes(
                            rec.file).decode('utf-8'))
                        myreader = csv.reader(file.splitlines())
                        skip_header = True
                        start_import = False
                        for row in myreader:
                            counter = counter + 1
                            try:
                                if start_import and not row[3] == 'Total':
                                    date_tr = False
                                    if row[1]:
                                        date_tr = str(datetime.strptime(row[1], '%d/%m/%Y').date())
                                    amt = 0
                                    if row[5]:
                                        amt = - float(row[5].replace(',',''))
                                    if row[6]:
                                        amt = float(row[6].replace(',',''))
                                    vals = {
                                        'date': date_tr,
                                        # 'name': str(row[3]),
                                        'payment_ref': str(row[3]),
                                        'amount': amt,
                                        'statement_id': self.env.context.get("sh_abs_id")
                                    }
                                    absl_obj.with_context(from_import=True).create(vals)
                                if row[1] == 'Date':
                                    start_import = True
                            except Exception as e:
                                error = 'error at row no ' + str(row)
                                raise UserError(error)
                    except Exception as e:
                        error = 'error at row no ' + str(counter) + ' - ' + str(e)
                        raise UserError(error)

                    # if counter > 1:
                    #     completed_bsl = (counter - len(skipped_line_no)) - 2
                    #     res = rec.show_success_msg(
                    #         completed_bsl, skipped_line_no)
                    #     return res

            #For Excel
            if self.import_type == 'excel':
                for rec in self:
                    counter = 1
                    skipped_line_no = {}
                    row_field_dic = {}
                    row_field_error_dic = {}
                    try:
                        wb = xlrd.open_workbook(
                            file_contents=base64.decodebytes(rec.file))
                        sheet = wb.sheet_by_index(0)
                        skip_header = True
                        for row in range(sheet.nrows):
                            try:
                                if skip_header:
                                    skip_header = False

                                    for i in range(6, sheet.ncols):
                                        name_field = sheet.cell(row, i).value
                                        name_m2o = False
                                        if '@' in sheet.cell(row, i).value:
                                            list_field_str = name_field.split(
                                                '@')
                                            name_field = list_field_str[0]
                                            name_m2o = list_field_str[1]
                                        search_field = ir_model_fields_obj.sudo().search([
                                            ("model", "=",
                                             "account.bank.statement.line"),
                                            ("name", "=", name_field),
                                            ("store", "=", True),
                                        ], limit=1)
                                        if search_field:
                                            field_dic = {
                                                'name': name_field,
                                                'ttype': search_field.ttype,
                                                'required': search_field.required,
                                                'name_m2o': name_m2o
                                            }
                                            row_field_dic.update(
                                                {i: field_dic})
                                        else:
                                            row_field_error_dic.update(
                                                {sheet.cell(row, i).value: " - field not found"})

                                    counter = counter + 1
                                    continue

                                if sheet.cell(row, 0).value != '' and sheet.cell(row, 1).value != '':
                                    final_date = None
                                    cd = sheet.cell(row, 0).value
                                    cd = str(datetime.strptime(
                                        cd, '%Y-%m-%d').date())
                                    final_date = cd

                                    search_partner_id = False
                                    if sheet.cell(row, 2).value != '':
                                        search_partner = self.env["res.partner"].search(
                                            [('name', '=', sheet.cell(row, 2).value)], limit=1)
                                        if search_partner:
                                            search_partner_id = search_partner.id
                                    vals = {
                                        'date': final_date,
                                        'name': sheet.cell(row, 1).value,
                                        'partner_id': search_partner_id,
                                        'ref': sheet.cell(row, 3).value,
                                        'amount': sheet.cell(row, 4).value,
                                        'payment_ref':sheet.cell(row, 1).value,
                                        'statement_id': self.env.context.get("sh_abs_id")
                                    }

                                    is_any_error_in_dynamic_field = False
                                    for k_row_index, v_field_dic in row_field_dic.items():

                                        field_name = v_field_dic.get("name")
                                        field_ttype = v_field_dic.get("ttype")
                                        field_value = sheet.cell(
                                            row, k_row_index).value
                                        field_required = v_field_dic.get(
                                            "required")
                                        field_name_m2o = v_field_dic.get(
                                            "name_m2o")

                                        dic = self.validate_field_value(
                                            field_name, field_ttype, field_value, field_required, field_name_m2o)
                                        if dic.get("error", False):
                                            skipped_line_no[str(counter)] = dic.get(
                                                "error")
                                            is_any_error_in_dynamic_field = True
                                            break
                                        else:
                                            vals.update(dic)

                                    if is_any_error_in_dynamic_field:
                                        counter = counter + 1
                                        continue

                                    absl_obj.create(vals)
                                    counter = counter + 1
                                else:
                                    skipped_line_no[str(
                                        counter)] = " - Date or Label is empty. "
                                    counter = counter + 1
                            except Exception as e:
                                skipped_line_no[str(
                                    counter)] = " - Value is not valid " + ustr(e)
                                counter = counter + 1
                                continue

                    except Exception:
                        raise UserError(
                            _("Sorry, Your excel file does not match with our format"))

                    if counter > 1:
                        completed_lead = (counter - len(skipped_line_no)) - 2
                        res = rec.show_success_msg(
                            completed_lead, skipped_line_no)
                        return res
