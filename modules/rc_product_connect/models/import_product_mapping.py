# Copyright (C) 2021 Honestus <http://www.honestus.lt>
# @author Tomas Karpovic <tomas.karpovic@honestus.lt>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


text_field_types = ["char", "html", "text"]


class ImportProductMapping(models.Model):
    _name = "import.product.mapping"
    _description = "Import Product Mapping"
    order = "name, id"

    name = fields.Char()
    product_template_field_id = fields.Many2one(
        "ir.model.fields",
        string="Product Template Field",
        domain=lambda self: [
            ("model_id", "=", self.env.ref("product.model_product_template").id),
            ("name", "!=", "name"),
        ],
    )
    import_product_table_field_id = fields.Many2one(
        "ir.model.fields",
        string="Import Product Table Field",
        domain=lambda self: [
            (
                "model_id",
                "=",
                self.env.ref("rc_product_connect.model_import_product_table").id,
            )
        ],
    )

    @api.onchange("product_template_field_id")
    def onchange_product_template_field_id(self):
        field = self.product_template_field_id
        domain = [
            (
                "model_id",
                "=",
                self.env.ref("rc_product_connect.model_import_product_table").id,
            ),
        ]
        if field:
            if field.ttype in text_field_types:
                available_types = text_field_types
            else:
                available_types = [field.ttype]
            domain.append(
                ("ttype", "in", available_types),
            )
        return {"domain": {"import_product_table_field_id": domain}}

    @api.onchange("import_product_table_field_id")
    def onchange_import_product_table_field_id(self):
        field = self.import_product_table_field_id
        domain = [
            (
                "model_id",
                "=",
                self.env.ref("product.model_product_template").id,
            ),
            ("name", "!=", "name"),
        ]
        if field:
            if field.ttype in text_field_types:
                available_types = text_field_types
            else:
                available_types = [field.ttype]
            domain.append(
                ("ttype", "in", available_types),
            )
        return {"domain": {"product_template_field_id": domain}}
