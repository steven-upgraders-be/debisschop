# Copyright (C) 2021 Honestus <http://www.honestus.lt>
# @author Tomas Karpovic <tomas.karpovic@honestus.lt>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


text_field_types = ["char", "html", "text"]


class ImportProductMapping(models.Model):
    _name = "import.product.mapping"
    order = "id"

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

    @api.constrains("product_template_field_id", "import_product_table_field_id")
    def _check_field_types(self):
        for mapping in self:
            if (
                mapping.product_template_field_id.ttype in text_field_types
                and mapping.import_product_table_field_id.ttype in text_field_types
            ):
                continue
            if (
                mapping.product_template_field_id.ttype
                != mapping.import_product_table_field_id.ttype
            ):
                raise ValidationError(_("Mapped fields should have same types."))
