# Copyright (C) 2021 Honestus <http://www.honestus.lt>
# @author Tomas Karpovic <tomas.karpovic@honestus.lt>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    pims_category_ids = fields.Many2many(
        "product.category.pims",
        related="company_id.pims_category_ids",
        readonly=False,
    )
    pims_attribute_ids = fields.Many2many(
        "product.category.attribute.pims",
        related="company_id.pims_attribute_ids",
        readonly=False,
    )
    products_url = fields.Char(related="company_id.products_url", readonly=False)
    product_name_field_id = fields.Many2one(
        related="company_id.product_name_field_id", readonly=False
    )
    import_product_mapping_ids = fields.Many2many(
        "import.product.mapping",
        related="company_id.import_product_mapping_ids",
        readonly=False,
    )
