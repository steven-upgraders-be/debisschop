# Copyright (C) 2021 Honestus <http://www.honestus.lt>
# @author Tomas Karpovic <tomas.karpovic@honestus.lt>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from urllib.request import urlopen
import lxml.etree as ET

from odoo import models, fields, _, api

from ..utils import get_errors_string, get_exception_error_string


class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    rc_category_code = fields.Char(string="RC Category ID")
    product_public_category_attribute_ids = fields.Many2many(
        "product.public.category.attribute",
        "product_public_category_attributes_rel",
        "category_id",
        "attribute_id",
        string="Attributes",
    )

    def _sync_rc_product_categories(self):
        self.sync_categories()
        # celery = {"countdown": 2}
        # self.env["celery.task"].call_task(
        #     "product.public.category",
        #     "sync_categories",
        #     celery=celery,
        #     transaction_strategy="immediate",
        # )

    def create_edit_categories(self, categories, level, errors, processed_categories):
        active_langs = (
            self.env["res.lang"].search([("active", "=", True)]).mapped("code")
        )

        for category_el in categories:
            rc_category_id = category_el.find("idCat_{}".format(level))
            nl_name = category_el.find("categorie_N").text
            fr_name = category_el.find("categorie_F").text
            parent_level = str(int(level) - 1)
            rc_parent_category_id = category_el.find("idCat_{}".format(parent_level))

            if not nl_name and not fr_name:
                errors.append(
                    get_exception_error_string(
                        level,
                        _("Name is not set for category with ID: {}").format(
                            rc_category_id.text
                        ),
                    )
                )
                continue

            vals = {"name": nl_name or fr_name, "rc_category_code": rc_category_id.text}
            if int(level) != 1 and rc_parent_category_id.text:
                parent_id = self.search(
                    [
                        (
                            "rc_category_code",
                            "=",
                            rc_parent_category_id.text,
                        )
                    ],
                    limit=1,
                )
                if parent_id:
                    vals["parent_id"] = parent_id.id

            category = self.search(
                [("rc_category_code", "=", rc_category_id.text)],
                limit=1,
            )
            if category:
                if (
                    vals["name"] != category.name
                    or vals.get("parent_id")
                    and vals["parent_id"] != category.parent_id.id
                ):
                    category.write(vals)
            else:
                category = self.create(vals)

            if "nl_BE" in active_langs and nl_name:
                category.with_context(lang="nl_BE").name = nl_name
            if "fr_BE" in active_langs and fr_name:
                category.with_context(lang="fr_BE").name = fr_name

            processed_categories.append(category.id)
        return errors, processed_categories

    @api.model
    def sync_categories(self):
        company = self.env.company
        product_category_levels = company.pims_category_ids
        errors = []
        processed_categories = []
        for l in product_category_levels:
            url = l.category_url
            level = l.sequence
            categories = []
            try:
                data = urlopen(url).read()
                data_tree = ET.fromstring(data)
                categories = data_tree.findall("Product")
            except Exception as e:
                errors.append(get_exception_error_string(level, e))
            errors, processed_categories = self.create_edit_categories(
                categories, level, errors, processed_categories
            )

        res = {
            "result": _("Categories successfully imported/edited in Odoo."),
            "res_model": "product.public.category",
        }
        if not processed_categories:
            res["result"] = _(
                "Categories were not imported/edited. "
                "Please check source file location settings."
            )
        if errors:
            res["result"] = _(
                "Some categories successfully imported/edited in Odoo.\n"
                "Some have failed:\n{error}"
            ).format(
                error=get_errors_string(errors),
            )
        return res
