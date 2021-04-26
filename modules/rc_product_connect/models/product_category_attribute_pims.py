# Copyright (C) 2021 Honestus <http://www.honestus.lt>
# @author Mantas Kalytis <mantas.kalytis@honestus.lt>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, fields


class ProductCategoryAttributePims(models.Model):
    _name = "product.category.attribute.pims"
    _description = "Product Category Attribute Pims"

    order = "sequence"

    sequence = fields.Integer("Sequence", default=1, required=True)
    attribute_url = fields.Char(required=True)
