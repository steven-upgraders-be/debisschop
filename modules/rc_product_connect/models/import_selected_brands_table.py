# Copyright (C) 2021 Honestus <http://www.honestus.lt>
# @author Tomas Karpovic <tomas.karpovic@honestus.lt>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, fields


class ImportSelectedBrandsTable(models.Model):
    _name = "import.selected.brands.table"
    _order = "name, id"

    name = fields.Char()
    brand_selected_for_import = fields.Boolean()
    brand_is_active = fields.Boolean()
    supplier = fields.Char()
    import_product_ids = fields.One2many(
        "import.product.table", "brand_id", string="Import Products"
    )

    _sql_constraints = [("name_uniq", "unique(name)", "A brand name should be unique!")]

    def write(self, vals):
        result = super(ImportSelectedBrandsTable, self).write(vals)
        if "brand_selected_for_import" in vals:
            for brand in self:
                brand.import_product_ids.write(
                    {"product_selected_for_import": brand.brand_selected_for_import}
                )
        return result
