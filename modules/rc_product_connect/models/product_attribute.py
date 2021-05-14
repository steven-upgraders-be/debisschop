# Copyright (C) 2021 Honestus <http://www.honestus.lt>
# @author Tomas Karpovic <tomas.karpovic@honestus.lt>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from urllib.request import urlopen
import lxml.etree as ET
import psycopg2

from odoo import models, fields, _, api

from ..utils import get_errors_string, get_exception_error_string


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    def _sync_rc_category_attributes(self):
        self.sync_category_attributes()

    def create_edit_attributes(
        self,
        attributes,
        number,
        errors,
        processed_attribute_values,
    ):
        active_langs = (
            self.env["res.lang"].search([("active", "=", True)]).mapped("code")
        )
        attribute_value_obj = self.env["product.attribute.value"]

        empty_attribute_id_count = 0

        for attribute_el in attributes:
            rc_attribute_value_id = attribute_el.find("id")
            rc_category_level3_id = attribute_el.find("parent")
            nl_name = attribute_el.find("attribuut_N").text
            fr_name = attribute_el.find("attribuut_F").text
            nl_attribute_name = attribute_el.find("label_N").text
            fr_attribute_name = attribute_el.find("label_F").text
            sequence = attribute_el.find("sort").text

            if not rc_attribute_value_id.text:
                empty_attribute_id_count += 1
                continue

            if not nl_name and not fr_name:
                errors.append(
                    get_exception_error_string(
                        number,
                        _("Name is not set for attribute value with ID: {}").format(
                            rc_attribute_value_id.text
                        ),
                        source="attribute",
                    )
                )
                continue

            if not nl_attribute_name and not fr_attribute_name:
                errors.append(
                    get_exception_error_string(
                        number,
                        _("Label is not set for attribute with ID: {}").format(
                            rc_attribute_value_id.text
                        ),
                        source="attribute",
                    )
                )
                continue

            attribute_vals = {
                "name": nl_attribute_name or fr_attribute_name,
                "create_variant": "no_variant",
            }

            attribute = self.search(
                [("name", "=", nl_attribute_name or fr_attribute_name)], limit=1
            )
            if attribute:
                attribute.write(attribute_vals)
            else:
                attribute = self.create(attribute_vals)

            if "nl_BE" in active_langs and nl_attribute_name:
                attribute.with_context(lang="nl_BE").name = nl_attribute_name
            if "fr_BE" in active_langs and fr_attribute_name:
                attribute.with_context(lang="fr_BE").name = fr_attribute_name

            attribute_value_vals = {
                "name": nl_name or fr_name,
                "rc_attribute_value_id": rc_attribute_value_id.text,
                "attribute_id": attribute.id,
                "sequence": sequence,
            }
            if rc_category_level3_id.text:
                rc_category_level3 = self.env["product.public.category"].search(
                    [("rc_category_code", "=", rc_category_level3_id.text)], limit=1
                )
                if rc_category_level3:
                    attribute_value_vals["product_public_category_ids"] = [
                        (4, rc_category_level3.id)
                    ]

            attribute_value = attribute_value_obj.search(
                [
                    ("rc_attribute_value_id", "=", rc_attribute_value_id.text),
                    ("attribute_id", "=", attribute.id),
                ],
                limit=1,
            )
            try:
                if attribute_value:
                    attribute_value.write(attribute_value_vals)
                else:
                    attribute_value = attribute_value_obj.create(attribute_value_vals)
                self.env.cr.commit()
            except psycopg2.DatabaseError as e:
                self.env.cr.rollback()
                pgerror = getattr(e, "pgerror")
                if pgerror and "duplicate key" in pgerror:
                    e = _(
                        "Duplicate contstraint violation! Attribute value with name: "
                        "'{value_name}' already exists for "
                        "attribute (label): '{attribute_name}'. Each attribute should "
                        "have attribute values with unique names."
                    ).format(
                        value_name=attribute_value_vals["name"],
                        attribute_name=attribute_vals["name"],
                    )
                errors.append(get_exception_error_string(number, e, source="attribute"))
            except Exception as e:
                errors.append(get_exception_error_string(number, e, source="attribute"))

            if "nl_BE" in active_langs and nl_name:
                attribute_value.with_context(lang="nl_BE").name = nl_name
            if "fr_BE" in active_langs and fr_name:
                attribute_value.with_context(lang="fr_BE").name = fr_name
            processed_attribute_values.append(attribute_value.id)

        if empty_attribute_id_count > 0:
            errors.append(
                get_exception_error_string(
                    number,
                    _("Found {} attribute velues with empty ID.").format(
                        empty_attribute_id_count,
                    ),
                    source="attribute",
                )
            )
        return errors, processed_attribute_values

    @api.model
    def sync_category_attributes(self):
        company = self.env.company
        attributes = company.pims_attribute_ids
        errors = []
        processed_attribute_values = []
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
                    processed_attribute_values,
                )

        result = _("Category level 3 attributes successfully imported/edited in Odoo.")
        if not processed_attribute_values:
            result = _(
                "Category level 3 attributes were not imported/edited. "
                "Please check source file location settings."
            )
        if errors:
            result = _(
                "Some category level 3 attributes successfully imported/edited "
                "in Odoo.\n"
                "Some have failed:\n{error}"
            ).format(
                error=get_errors_string(errors),
            )
        self.env["mail.channel"].post_system_message(result)
        return True


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    rc_attribute_value_id = fields.Char("RC Attribute Value ID")
    product_public_category_ids = fields.Many2many(
        "product.public.category",
        "product_public_category_product_attribute_value_rel",
        "attribute_value_id",
        "category_id",
        string="Categories",
    )
