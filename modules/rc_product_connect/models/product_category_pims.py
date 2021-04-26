# Copyright (C) 2021 Honestus <http://www.honestus.lt>
# @author Mantas Kalytis <mantas.kalytis@honestus.lt>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, fields


class ProductCategoryPims(models.Model):
    _name = "product.category.pims"
    _description = "Product Category Pims"

    order = "sequence"

    sequence = fields.Integer("Sequence", default=1, required=True)
    category_url = fields.Char(required=True)
