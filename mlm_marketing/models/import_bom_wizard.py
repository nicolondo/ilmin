# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models, _
from odoo.exceptions import UserError
import csv
import base64
import xlrd
import logging
import json


_logger = logging.getLogger(__name__)


class ImportBSLWizard(models.TransientModel):
    _name = "mlm_marketing.bom.wizard"
    _description = "Import Bom Wizard"

    file = fields.Binary(string="File", required=True)

    def import_bom_apply(self):
        productTmplObj = self.env['product.template']
        productObj = self.env['product.product']
        bomObj = self.env['mrp.bom']

        #perform import lead
        if self and self.file:

            #For Excel
            for rec in self:
                counter = 1
                skipped_line_no = {}
                try:
                    wb = xlrd.open_workbook(
                        file_contents=base64.decodebytes(rec.file))
                    sheet = wb.sheet_by_index(0)
                    for row in range(1,sheet.nrows):
                        try:
                            if sheet.cell(row, 0).value != '' and sheet.cell(row, 1).value != '' and sheet.cell(row, 3).value != '':
                                product_tmpl = productTmplObj.search([('default_code','=',sheet.cell(row, 0).value)])
                                if not product_tmpl :
                                    counter = counter + 1
                                    skipped_line_no[str(
                                        counter)] = "Product not found %s" %sheet.cell(row, 0).value
                                    continue

                                bom = bomObj.search(
                                        [('product_tmpl_id', '=', product_tmpl.id),('product_qty', '=', 1)], limit=1)

                                if not bom :
                                    bom = self.env['mrp.bom'].create({
                                        'product_tmpl_id': product_tmpl.id,
                                        'product_qty': 1,
                                        'type': 'normal',
                                    })

                                product_bom_line = productObj.search([('default_code','=',sheet.cell(row, 1).value)])

                                if not product_bom_line:
                                    is_any_error = True
                                    skipped_line_no[str(
                                        counter)] = "Product not found %s" % sheet.cell(row, 1).value
                                    counter = counter + 1
                                    continue

                                bom_line = self.env['mrp.bom.line'].search(
                                    [('bom_id', '=', bom.id), ('product_id', '=', product_bom_line.id)])

                                if bom_line:
                                    bom_line.update({
                                        'product_qty': float(sheet.cell(row, 3).value),
                                    })
                                else:
                                    self.env['mrp.bom.line'].create({
                                        'bom_id': bom.id,
                                        'product_id': product_bom_line.id,
                                        'product_qty': float(sheet.cell(row, 3).value),
                                    })


                                counter = counter + 1
                            else:
                                skipped_line_no[str(
                                    counter)] = " - Data is empty. "
                                counter = counter + 1
                        except Exception as e:
                            skipped_line_no[str(
                                counter)] = " - Value is not valid " + str(e)
                            counter = counter + 1
                            continue

                except Exception:
                    raise UserError(
                        _("Sorry, Your excel file does not match with our format"))

                if len(skipped_line_no) > 1:
                    raise UserError(
                        json.dumps(skipped_line_no, indent = 4))
                else :
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'reload',
                    }