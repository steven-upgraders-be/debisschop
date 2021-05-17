# Copyright (C) 2021 Honestus <http://www.honestus.lt>
# @author Tomas Karpovic <tomas.karpovic@honestus.lt>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from urllib.request import urlopen
from urllib.parse import urlparse
import lxml.etree as ET
from datetime import datetime
import psycopg2

from odoo import models, fields, _, api
from odoo.tools.translate import html_translate

from ..utils import get_errors_string, get_exception_error_string, isfloat


FIELDS_TO_TRANSLATE = [
    "productTitel",
    "productInfo",
    "productBeschrijving",
    "URL_PDF",
    "URL_LEV",
]


def invalid_float_error(field, ean):
    return get_exception_error_string(
        "",
        _("Invalid {field} float value for product with EAN code: {ean}").format(
            field=field,
            ean=ean.text,
        ),
        source="product",
    )


def try_parsing_date(date_string):
    for fmt in ("%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M"):
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            pass
    return False


def url_validator(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc, result.path])
    except:
        return False


class ImportProductTable(models.Model):
    _name = "import.product.table"
    _description = "Import Product Table"
    _order = "productBeschrijving, id"

    idArtikel = fields.Char("idArtikel")
    artikelnummer = fields.Char()
    typenummer = fields.Char()
    ean = fields.Char("EAN", readonly=True)
    brand_id = fields.Many2one("import.selected.brands.table", "Brand")
    merk = fields.Char()
    merk_origineel = fields.Char()
    rrp = fields.Float("RRP")
    taksen = fields.Float()
    vkp = fields.Float("VKP")
    productTitel = fields.Char(translate=True)
    productInfo = fields.Html(translate=html_translate)
    productBeschrijving = fields.Char(translate=True)
    idCat_1 = fields.Integer("Product Category Level 1 ID")
    idCat_2 = fields.Integer("Product Category Level 2 ID")
    idCat_3 = fields.Integer("Product Category Level 3 ID")
    URL_afbeelding_1 = fields.Char()
    URL_afbeelding_2 = fields.Char()
    URL_afbeelding_3 = fields.Char()
    URL_afbeelding_4 = fields.Char()
    URL_afbeelding_5 = fields.Char()
    URL_PDF = fields.Char(translate=True)
    URL_LEV = fields.Char(translate=True)
    accessoires = fields.Char()
    status = fields.Integer()
    update_trigger = fields.Datetime(readonly=True)
    product_selected_for_import = fields.Boolean()
    product_is_active = fields.Boolean()
    idAtt_01 = fields.Integer()
    idAtt_02 = fields.Integer()
    idAtt_03 = fields.Integer()
    idAtt_04 = fields.Integer()
    idAtt_05 = fields.Integer()
    idAtt_06 = fields.Integer()
    idAtt_07 = fields.Integer()
    idAtt_08 = fields.Integer()
    idAtt_09 = fields.Integer()
    idAtt_10 = fields.Integer()
    idAtt_11 = fields.Integer()
    idAtt_12 = fields.Integer()
    idAtt_13 = fields.Integer()
    idAtt_14 = fields.Integer()
    idAtt_15 = fields.Integer()

    def _sync_rc_import_product_table(self):
        self.sync_rc_import_product_table()

    def _create_edit_products(self):
        self.create_edit_products()

    def create_edit_import_products(
        self,
        products,
        errors,
        processed_products,
    ):
        active_langs = (
            self.env["res.lang"].search([("active", "=", True)]).mapped("code")
        )
        translation_obj = self.env["ir.translation"]

        brand_obj = self.env["import.selected.brands.table"]

        existing_products = self.search([("product_is_active", "=", True)])
        existing_products.write({"product_is_active": False})

        existing_brands = brand_obj.search([("brand_is_active", "=", True)])
        existing_brands.write({"brand_is_active": False})

        empty_ean_count = 0

        for product_el in products:
            default_el = product_el.find("default")
            nl_el = product_el.find("nl")
            fr_el = product_el.find("fr")
            nl_productTitel = (
                nl_productInfo
            ) = nl_productBeschrijving = nl_URL_PDF = nl_URL_LEV = ""
            fr_productTitel = (
                fr_productInfo
            ) = fr_productBeschrijving = fr_URL_PDF = fr_URL_LEV = ""
            if nl_el:
                nl_productTitel = nl_el.find("productTitel").text
                nl_productInfo = nl_el.find("productInfo").text
                nl_productBeschrijving = nl_el.find("productBeschrijving").text
                nl_URL_PDF = nl_el.find("URL_PDF").text
                nl_URL_LEV = nl_el.find("URL_LEV").text
            if fr_el:
                fr_productTitel = fr_el.find("productTitel").text
                fr_productInfo = fr_el.find("productInfo").text
                fr_productBeschrijving = fr_el.find("productBeschrijving").text
                fr_URL_PDF = fr_el.find("URL_PDF").text
                fr_URL_LEV = fr_el.find("URL_LEV").text
            ean = default_el.find("EAN")
            update_trigger_text = default_el.find("update_trigger").text
            merk_origineel = default_el.find("merk_origineel").text

            if not ean.text:
                empty_ean_count += 1
                continue

            vals = {
                "idArtikel": default_el.find("idArtikel").text,
                "artikelnummer": default_el.find("artikelnummer").text,
                "typenummer": default_el.find("typenummer").text,
                "ean": ean.text,
                "merk": default_el.find("merk").text,
                "merk_origineel": merk_origineel,
                "productTitel": nl_productTitel or fr_productTitel,
                "productInfo": nl_productInfo or fr_productInfo,
                "productBeschrijving": nl_productBeschrijving or fr_productBeschrijving,
                "idCat_1": default_el.find("idCat_1").text,
                "idCat_2": default_el.find("idCat_2").text,
                "idCat_3": default_el.find("idCat_3").text,
                "idAtt_01": default_el.find("idAtt_01").text,
                "idAtt_02": default_el.find("idAtt_02").text,
                "idAtt_03": default_el.find("idAtt_03").text,
                "idAtt_04": default_el.find("idAtt_04").text,
                "idAtt_05": default_el.find("idAtt_05").text,
                "idAtt_06": default_el.find("idAtt_06").text,
                "idAtt_07": default_el.find("idAtt_07").text,
                "idAtt_08": default_el.find("idAtt_08").text,
                "idAtt_09": default_el.find("idAtt_09").text,
                "idAtt_10": default_el.find("idAtt_10").text,
                "idAtt_11": default_el.find("idAtt_11").text,
                "idAtt_12": default_el.find("idAtt_12").text,
                "idAtt_13": default_el.find("idAtt_13").text,
                "idAtt_14": default_el.find("idAtt_14").text,
                "idAtt_15": default_el.find("idAtt_15").text,
                "URL_afbeelding_1": default_el.find("URL_afbeelding_1").text,
                "URL_afbeelding_2": default_el.find("URL_afbeelding_2").text,
                "URL_afbeelding_3": default_el.find("URL_afbeelding_3").text,
                "URL_afbeelding_4": default_el.find("URL_afbeelding_4").text,
                "URL_afbeelding_5": default_el.find("URL_afbeelding_5").text,
                "URL_PDF": nl_URL_PDF or fr_URL_PDF,
                "URL_LEV": nl_URL_LEV or fr_URL_LEV,
                "accessoires": default_el.find("accessoires").text,
                "status": default_el.find("status").text,
                "product_is_active": True,
            }

            brand = brand_obj.search([("name", "=", merk_origineel)])
            if not brand:
                brand = brand_obj.create(
                    {"name": merk_origineel, "supplier": "Royal Crown"}
                )
            brand.brand_is_active = True
            vals["brand_id"] = brand.id
            if brand.brand_selected_for_import:
                vals["product_selected_for_import"] = True

            if update_trigger_text:
                update_trigger = try_parsing_date(update_trigger_text)
                if update_trigger:
                    vals["update_trigger"] = update_trigger
                else:
                    errors.append(
                        get_exception_error_string(
                            "",
                            _(
                                "Update trigger date format is invalid for "
                                "product with EAN code: {}."
                            ).format(
                                ean.text,
                            ),
                            source="product",
                        )
                    )

            rrp = (
                default_el.find("RRP").text
                and default_el.find("RRP").text.replace(",", ".")
                or "0.0"
            )
            taksen = (
                default_el.find("taksen").text
                and default_el.find("taksen").text.replace(",", ".")
                or "0.0"
            )
            vkp = (
                default_el.find("VKP").text
                and default_el.find("VKP").text.replace(",", ".")
                or "0.0"
            )

            if rrp and not isfloat(rrp):
                errors.append(invalid_float_error("RRP", ean))
            else:
                vals["rrp"] = rrp

            if taksen and not isfloat(taksen):
                errors.append(invalid_float_error("Taksen", ean))
            else:
                vals["taksen"] = taksen

            if vkp and not isfloat(vkp):
                errors.append(invalid_float_error("VKP", ean))
            else:
                vals["vkp"] = vkp

            product = self.search([("ean", "=", ean.text)], limit=1)
            if product:
                product.write(vals)
            else:
                product = self.create(vals)

            if "nl_BE" in active_langs:
                if nl_productTitel:
                    product.with_context(lang="nl_BE").productTitel = nl_productTitel
                if nl_productInfo:
                    # removing existing translation of html field
                    translation_obj.search(
                        [
                            ("name", "=", "import.product.table,productInfo"),
                            ("res_id", "=", product.id),
                            ("lang", "=", "nl_BE"),
                            ("state", "=", "translated"),
                        ]
                    ).unlink()
                    self.env.cr.commit()
                    try:
                        translation_obj.create(
                            {
                                "src": vals["productInfo"],
                                "value": nl_productInfo,
                                "type": "model_terms",
                                "name": "import.product.table,productInfo",
                                "res_id": product.id,
                                "lang": "nl_BE",
                                "state": "translated",
                            }
                        )
                        self.env.cr.commit()
                    except psycopg2.DatabaseError as e:
                        self.env.cr.rollback()
                        pass
                if nl_productBeschrijving:
                    product.with_context(
                        lang="nl_BE"
                    ).productBeschrijving = nl_productBeschrijving
                if nl_URL_PDF:
                    product.with_context(lang="nl_BE").URL_PDF = nl_URL_PDF
                if nl_URL_LEV:
                    product.with_context(lang="nl_BE").URL_LEV = nl_URL_LEV
            if "fr_BE" in active_langs:
                if fr_productTitel:
                    product.with_context(lang="fr_BE").productTitel = fr_productTitel
                if fr_productInfo:
                    # removing existing translation of html field
                    translation_obj.search(
                        [
                            ("name", "=", "import.product.table,productInfo"),
                            ("res_id", "=", product.id),
                            ("lang", "=", "fr_BE"),
                            ("state", "=", "translated"),
                        ]
                    ).unlink()
                    self.env.cr.commit()
                    try:
                        translation_obj.create(
                            {
                                "src": vals["productInfo"],
                                "value": fr_productInfo,
                                "type": "model_terms",
                                "name": "import.product.table,productInfo",
                                "res_id": product.id,
                                "lang": "fr_BE",
                                "state": "translated",
                            }
                        )
                        self.env.cr.commit()
                    except psycopg2.DatabaseError as e:
                        self.env.cr.rollback()
                        pass
                if fr_productBeschrijving:
                    product.with_context(
                        lang="fr_BE"
                    ).productBeschrijving = fr_productBeschrijving
                if fr_URL_PDF:
                    product.with_context(lang="fr_BE").URL_PDF = fr_URL_PDF
                if fr_URL_LEV:
                    product.with_context(lang="fr_BE").URL_LEV = fr_URL_LEV

            processed_products.append(product.id)

        if empty_ean_count > 0:
            errors.append(
                get_exception_error_string(
                    "",
                    _("Found {} products with empty EAN code.").format(
                        empty_ean_count,
                    ),
                    source="product",
                )
            )
        return errors, processed_products

    @api.model
    def sync_rc_import_product_table(self):
        company = self.env.company
        url = company.products_url
        errors = []
        processed_products = []

        if url:
            products = []
            try:
                data = urlopen(url).read()
                data_tree = ET.fromstring(data)
                products = data_tree.findall("product")
            except Exception as e:
                errors.append(get_exception_error_string("", e, source="product"))
            errors, processed_products = self.create_edit_import_products(
                products,
                errors,
                processed_products,
            )

        result = _("Products successfully imported/edited in Odoo.")
        if not processed_products:
            result = _(
                "Products were not imported/edited. "
                "Please check source file location settings."
            )
        if errors:
            result = _(
                "Some products successfully imported/edited in Odoo.\n"
                "Some have failed:\n{error}"
            ).format(
                error=get_errors_string(errors),
            )
        self.env["mail.channel"].post_system_message(result)
        return True

    def process_create_edit_products(self, processed_products, errors):
        active_langs = (
            self.env["res.lang"].search([("active", "=", True)]).mapped("code")
        )
        translation_obj = self.env["ir.translation"]
        product_tmpl_obj = self.env["product.template"]
        product_image_obj = self.env["product.image"]
        product_public_category_obj = self.env["product.public.category"]

        company = self.env.company
        product_name_field = company.product_name_field_id
        import_product_mappings = company.import_product_mapping_ids
        import_extra_image_mappings = company.import_extra_image_mapping_ids
        import_eshop_categories_mappings = company.import_eshop_category_mapping_ids

        # searching for products to import
        import_products_to_process = self.search(
            [
                ("product_selected_for_import", "=", True),
                ("product_is_active", "=", True),
            ]
        )
        for import_product in import_products_to_process:
            ean = import_product.ean
            self.env.cr.commit()
            try:
                # basic vals
                vals = {
                    "name": getattr(
                        import_product.with_context(lang="nl_BE"),
                        product_name_field.name,
                    ),
                    "ean": ean,
                    "type": "product",
                    "rc_last_update_date": import_product.update_trigger,
                }
                # getting vals by mapping
                for mapping in import_product_mappings:
                    vals[mapping.product_template_field_id.name] = getattr(
                        import_product.with_context(lang="nl_BE"),
                        mapping.import_product_table_field_id.name,
                    )

                # parsing images from url
                images = []
                for image_mapping in import_extra_image_mappings:
                    image_url = getattr(
                        import_product, image_mapping.image_url_field_id.name
                    )

                    if image_url and url_validator(image_url):
                        extra_image = product_image_obj.create(
                            {"name": image_url, "image_url": image_url}
                        )
                        extra_image._onchange_image_url()
                        images.append((4, extra_image.id))
                if images:
                    vals["product_template_image_ids"] = images

                # searching for categories to assign
                categories = []
                for category_mapping in import_eshop_categories_mappings:
                    category_id = getattr(
                        import_product, category_mapping.eshop_category_field_id.name
                    )
                    if category_id:
                        category = product_public_category_obj.search(
                            [("rc_category_code", "=", category_id)],
                            limit=1,
                        )
                        if category and category.exists():
                            categories.append((4, category.id))
                if categories:
                    vals["public_categ_ids"] = categories

                # searching for attribute values to assign
                attribute_value_rc_ids = []
                for number in range(15):
                    number += 1
                    attribute_value_rc_id = getattr(
                        import_product,
                        "idAtt_{number}".format(number="{:02d}".format(number)),
                    )
                    if attribute_value_rc_id:
                        attribute_value_rc_ids.append(attribute_value_rc_id)

                attribute_values = self.env["product.attribute.value"]
                if attribute_value_rc_ids:
                    attribute_values = self.env["product.attribute.value"].search(
                        [("rc_attribute_value_id", "in", attribute_value_rc_ids)]
                    )

                    # error is raised when some of attribute values are not found in
                    # system
                    not_found_attribute_value_ids = set(
                        [str(v) for v in attribute_value_rc_ids]
                    ) - set(attribute_values.mapped("rc_attribute_value_id"))
                    if not_found_attribute_value_ids:
                        errors.append(
                            get_exception_error_string(
                                "",
                                _(
                                    "While assigning attribute values for "
                                    "product with EAN code: {ean}, this attribute "
                                    "value IDS was not found in "
                                    "system: {attribute_value_ids}."
                                ).format(
                                    ean=ean,
                                    attribute_value_ids=", ".join(
                                        not_found_attribute_value_ids
                                    ),
                                ),
                                source="product",
                            )
                        )

                product_template = product_tmpl_obj.search(
                    [("ean", "=", import_product.ean)], limit=1
                )

                action_done = False
                if product_template:
                    if (
                        product_template.rc_last_update_date
                        < import_product.update_trigger
                    ):
                        product_template.write(vals)
                        action_done = True
                else:
                    product_template = product_tmpl_obj.create(vals)
                    action_done = True
                if action_done:
                    if attribute_values:
                        attribute_line_ids = []
                        product_template.attribute_line_ids.unlink()
                        for attribute in attribute_values.mapped("attribute_id"):
                            attribute_line_ids.append(
                                (
                                    0,
                                    0,
                                    {
                                        "attribute_id": attribute.id,
                                        "value_ids": [
                                            (
                                                6,
                                                0,
                                                attribute_values.filtered(
                                                    lambda v: v.attribute_id == attribute
                                                ).ids,
                                            )
                                        ],
                                    },
                                )
                            )
                        product_template.attribute_line_ids = attribute_line_ids

                    product_template._onchange_image_url()
                    if not product_template.is_published:
                        product_template.website_publish_button()

                    # translation of fields which needs to be translated
                    for mapping in import_product_mappings:
                        if (
                            mapping.import_product_table_field_id.name
                            in FIELDS_TO_TRANSLATE
                        ):
                            for lang in active_langs:
                                if (
                                    mapping.import_product_table_field_id.ttype
                                    == "html"
                                ):
                                    # removing existing translation of html field
                                    translation_obj.search(
                                        [
                                            (
                                                "name",
                                                "=",
                                                "product.template,{}".format(
                                                    mapping.product_template_field_id.name
                                                ),
                                            ),
                                            ("res_id", "=", product_template.id),
                                            ("lang", "=", lang),
                                        ]
                                    ).unlink()
                                    self.env.cr.commit()

                                    translation = translation_obj.search(
                                        [
                                            (
                                                "name",
                                                "=",
                                                "import.product.table,{}".format(
                                                    mapping.import_product_table_field_id.name
                                                ),
                                            ),
                                            ("res_id", "=", import_product.id),
                                            ("lang", "=", lang),
                                            ("state", "=", "translated"),
                                        ],
                                        limit=1,
                                    )
                                    if translation:
                                        self.env.cr.commit()
                                        try:
                                            translation.copy(
                                                {
                                                    "name": "product.template,{}".format(
                                                        mapping.product_template_field_id.name
                                                    ),
                                                    "res_id": product_template.id,
                                                    "state": "translated"
                                                }
                                            )
                                            self.env.cr.commit()
                                        except psycopg2.DatabaseError as e:
                                            self.env.cr.rollback()
                                            pass
                                else:
                                    product_template.with_context(lang=lang).write(
                                        {
                                            mapping.product_template_field_id.name: getattr(
                                                import_product.with_context(lang=lang),
                                                mapping.import_product_table_field_id.name,
                                            )
                                        }
                                    )
                    for lang in active_langs:
                        product_template.with_context(lang=lang).name = getattr(
                            import_product.with_context(lang=lang),
                            product_name_field.name,
                        )

                processed_products.append(product_template.id)
                self.env.cr.commit()
            except psycopg2.DatabaseError as e:
                self.env.cr.rollback()
                errors.append(
                    get_exception_error_string(ean, e, source="product_template")
                )
            except Exception as e:
                errors.append(
                    get_exception_error_string(ean, e, source="product_template")
                )
        return processed_products, errors

    def create_edit_products(self):
        company = self.env.company
        product_name_field = company.product_name_field_id

        errors = []
        processed_products = []

        if not product_name_field:
            errors.append(
                get_exception_error_string(
                    "",
                    _(
                        "Mapping for product name is not set, please check "
                        "mapping settings screen.\n"
                    ),
                    source="product_template",
                )
            )

        try:
            processed_products, errors = self.process_create_edit_products(
                processed_products, errors
            )
        except Exception as e:
            errors.append(get_exception_error_string("", e, source="product_template"))

        result = _(
            "Products successfully created/edited and published in Odoo web shop."
        )
        if not processed_products:
            result = _(
                "Products were not created/edited. Please check mapping settings."
            )
        if errors:
            result = _(
                "Some products successfully created/edited "
                "and published in Odoo web shop.\n"
                "Some have failed:\n{error}"
            ).format(
                error=get_errors_string(errors),
            )
        self.env["mail.channel"].post_system_message(result)
        return True
