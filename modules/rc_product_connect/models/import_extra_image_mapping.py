# Copyright (C) 2021 Honestus <http://www.honestus.lt>
# @author Tomas Karpovic <tomas.karpovic@honestus.lt>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, fields, api


class ImportExtraImageMapping(models.Model):
    _name = "import.extra.image.mapping"
    _description = "Import Extra Image Mapping"
    order = "name, id"

    name = fields.Char()
    image_url_field_id = fields.Many2one(
        "ir.model.fields",
        string="Import Product Table Field (Image URL)",
        domain=lambda self: [
            (
                "model_id",
                "=",
                self.env.ref("rc_product_connect.model_import_product_table").id,
            ),
            ("ttype", "=", "char"),
        ],
    )
