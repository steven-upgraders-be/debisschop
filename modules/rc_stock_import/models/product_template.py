# Copyright (C) 2021 Honestus <http://www.honestus.lt>
# @author Tomas Karpovic <tomas.karpovic@honestus.lt>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import ftplib
from collections import defaultdict
import xlrd
import psycopg2

from odoo import models, _, api

from ..utils import get_errors_string, get_exception_error_string


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _sync_rc_stock(self):
        self.sync_rc_stock()

    def update_products_stock(
        self,
        stock_dict,
        errors,
    ):
        not_found_ean = []
        for ean, stock in stock_dict.items():
            product_template = self.search([("ean", "=", ean)], limit=1)
            if product_template:
                self.env.cr.commit()
                try:
                    warehouse = self.env["stock.warehouse"].search(
                        [("company_id", "=", self.env.company.id)], limit=1
                    )
                    # Before creating a new quant, the quant `create` method will check
                    # if it exists already. If it does, it'll edit its
                    # `inventory_quantity` instead of create a new one.
                    self.env["stock.quant"].with_context(inventory_mode=True).create(
                        {
                            "product_id": product_template.product_variant_id.id,
                            "location_id": warehouse.lot_stock_id.id,
                            "inventory_quantity": stock,
                        }
                    )
                    self.env.cr.commit()
                except psycopg2.DatabaseError as e:
                    self.env.cr.rollback()
                    errors.append(get_exception_error_string(ean, e))
                except Exception as e:
                    errors.append(get_exception_error_string(ean, e))
            else:
                not_found_ean.append(ean)
        if not_found_ean:
            errors.append(
                get_exception_error_string(
                    "",
                    _(
                        "System was unable to find products "
                        "with EAN codes:\n {}".format(", ".join(not_found_ean))
                    ),
                )
            )
        return errors

    @api.model
    def sync_rc_stock(self):
        company = self.env.company
        ftp_server = company.ftp_server
        ftp_username = company.ftp_username
        ftp_password = company.ftp_password
        filename = company.filename
        errors = []
        critical_issue = False

        if not ftp_server:
            errors.append(
                get_exception_error_string("", _("FTP Server is not set in settings."))
            )
            critical_issue = True
        if not ftp_username:
            errors.append(
                get_exception_error_string(
                    "", _("FTP Username is not set in settings.")
                )
            )
            critical_issue = True
        if not ftp_password:
            errors.append(
                get_exception_error_string(
                    "", _("FTP Password is not set in settings.")
                )
            )
            critical_issue = True
        if not filename:
            errors.append(
                get_exception_error_string(
                    "", _("Filename of XLSX file is not set in settings.")
                )
            )
            critical_issue = True

        if not critical_issue:
            stock_dict = defaultdict(lambda: 0.0)
            try:
                ftp = ftplib.FTP(ftp_server, ftp_username, ftp_password)

                filename_split = filename.split("/")
                if len(filename_split) > 1:
                    ftp.cwd(filename.replace(filename_split[-1], ""))
                    filename = filename_split[-1]

                if filename in ftp.nlst():
                    downloaded_file = open(filename, "wb")
                    ftp.retrbinary("RETR {}".format(filename), downloaded_file.write)
                    downloaded_file.close()
                    ftp.quit()

                    excel_file = xlrd.open_workbook(filename)
                    sheet = excel_file.sheet_by_index(0)

                    row_count = sheet.nrows
                    for cur_row in range(1, row_count):
                        ean = sheet.cell(cur_row, 1)
                        stock = sheet.cell(cur_row, 2)
                        stock_dict[ean.value] = stock.value
                else:
                    errors.append(
                        get_exception_error_string(
                            "", _("Filename is not found in provided FTP server.")
                        )
                    )
                    critical_issue = True
            except Exception as e:
                errors.append(get_exception_error_string("", e))
            errors = self.update_products_stock(
                stock_dict,
                errors,
            )

        result = _("Stock for products was successfully updated/imported in Odoo.")
        if critical_issue:
            result = _(
                "Stock for products was not updated/imported. "
                "Please check FTP settings.\n{error}"
            ).format(
                error=get_errors_string(errors),
            )
        if errors and not critical_issue:
            result = _(
                "Stock for some products was successfully updated/imported "
                "in Odoo.\n"
                "Some have failed:\n{error}"
            ).format(
                error=get_errors_string(errors),
            )
        self.env["mail.channel"].post_system_message(result)
        return True
