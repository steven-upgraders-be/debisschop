# Copyright (C) 2021 Honestus <http://www.honestus.lt>
# @author Tomas Karpovic <tomas.karpovic@honestus.lt>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, fields, api


class ImportEshopCategoryMapping(models.Model):
    _name = "import.eshop.category.mapping"
    order = "name, id"

    name = fields.Char()
    eshop_category_field_id = fields.Many2one(
        "ir.model.fields",
        string="Import Product Table Field (eCommerce Category ID)",
        domain=lambda self: [
            (
                "model_id",
                "=",
                self.env.ref("rc_product_connect.model_import_product_table").id,
            ),
            ("ttype", "=", "integer"),
        ],
    )
