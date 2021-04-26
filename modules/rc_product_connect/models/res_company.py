# Copyright (C) 2021 Honestus <http://www.honestus.lt>
# @author Tomas Karpovic <tomas.karpovic@honestus.lt>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    pims_category_ids = fields.Many2many("product.category.pims")
    pims_attribute_ids = fields.Many2many("product.category.attribute.pims")
    products_url = fields.Char()
    product_name_field_id = fields.Many2one(
        "ir.model.fields",
        string="Product Name Field",
        domain=lambda self: [
            (
                "model_id",
                "=",
                self.env.ref("rc_product_connect.model_import_product_table").id,
            ),
            ("ttype", "=", "char"),
        ],
    )
    import_product_mapping_ids = fields.Many2many("import.product.mapping")
