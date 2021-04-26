# Copyright (C) 2021 Honestus <http://www.honestus.lt>
# @author Tomas Karpovic <tomas.karpovic@honestus.lt>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from urllib.request import urlopen
import lxml.etree as ET

from odoo import models, fields, _, api

from ..utils import get_errors_string, get_exception_error_string


class ProductPublicCategoryAttribute(models.Model):
    _name = "product.public.category.attribute"
    _order = "sequence, name, id"

    name = fields.Char(required=True, translate=True)
    attribute_code = fields.Char()
    rc_attribute_code = fields.Char()
    sequence = fields.Integer(index=True)
    product_public_category_ids = fields.Many2many(
        "product.public.category",
        "product_public_category_attributes_rel",
        "attribute_id",
        "category_id",
        string="Categories",
    )

    def _sync_rc_category_attributes(self):
        self.sync_category_attributes()
        # celery = {"countdown": 2}
        # self.env["celery.task"].call_task(
        #     "product.public.category.attribute",
        #     "sync_category_attributes",
        #     celery=celery,
        # )

    def create_edit_attributes(
        self,
        attributes,
        number,
        errors,
        processed_attributes,
    ):
        active_langs = (
            self.env["res.lang"].search([("active", "=", True)]).mapped("code")
        )

        empty_attribute_id_count = 0

        for attribute_el in attributes:
            rc_attribute_id = attribute_el.find("id")
            attribute_code = attribute_el.find("attribute_code").text
            rc_category_level3_id = attribute_el.find("idCat3")
            nl_name = attribute_el.find("attribuut_N").text
            fr_name = attribute_el.find("attribuut_F").text
            sequence = attribute_el.find("sort").text

            if not rc_attribute_id.text or not attribute_code:
                empty_attribute_id_count += 1
                continue

            if not nl_name and not fr_name:
                errors.append(
                    get_exception_error_string(
                        number,
                        _("Name is not set for attribute with ID: {}").format(
                            rc_attribute_id.text
                        ),
                        source="attribute",
                    )
                )
                continue

            vals = {
                "name": nl_name or fr_name,
                "rc_attribute_code": rc_attribute_id.text,
                "attribute_code": attribute_code,
                "sequence": sequence,
            }

            if rc_category_level3_id.text:
                rc_category_level3 = self.env["product.public.category"].search(
                    [("rc_category_code", "=", rc_category_level3_id.text)], limit=1
                )
                if rc_category_level3:
                    vals["product_public_category_ids"] = [(4, rc_category_level3.id)]

            attribute = self.search(
                [
                    ("rc_attribute_code", "=", rc_attribute_id.text),
                    ("attribute_code", "=", attribute_code),
                ],
                limit=1,
            )
            if attribute:
                attribute.write(vals)
            else:
                attribute = self.create(vals)

            if "nl_BE" in active_langs and nl_name:
                attribute.with_context(lang="nl_BE").name = nl_name
            if "fr_BE" in active_langs and fr_name:
                attribute.with_context(lang="fr_BE").name = fr_name
            processed_attributes.append(attribute.id)

        if empty_attribute_id_count > 0:
            errors.append(
                get_exception_error_string(
                    number,
                    _("Found {} attributes with empty ID or attribute code.").format(
                        empty_attribute_id_count,
                    ),
                    source="attribute",
                )
            )
        return errors, processed_attributes

    @api.model
    def sync_category_attributes(self):
        company = self.env.company
        attributes = company.pims_attribute_ids
        errors = []
        processed_attributes = []
        for a in attributes:
            url = a.attribute_url
            number = a.sequence
            if url:
                attributes = []
                try:
                    data = urlopen(url).read()
                    data_tree = ET.fromstring(data)
                    attributes = data_tree.findall("Product")
                except Exception as e:
                    errors.append(
                        get_exception_error_string(number, e, source="attribute")
                    )
                errors, processed_categories = self.create_edit_attributes(
                    attributes,
                    number,
                    errors,
                    processed_attributes,
                )

        res = {
            "result": _(
                "Category level 3 attributes successfully imported/edited in Odoo."
            ),
            "res_model": "product.public.category.attribute",
        }
        if not processed_attributes:
            res["result"] = _(
                "Category level 3 attributes were not imported/edited. "
                "Please check source file location settings."
            )
        if errors:
            res["result"] = _(
                "Some category level 3 attributes successfully imported/edited "
                "in Odoo.\n"
                "Some have failed:\n{error}"
            ).format(
                error=get_errors_string(errors),
            )
        return res
