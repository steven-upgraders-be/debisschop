# Copyright (C) 2021 Honestus <http://www.honestus.lt>
# @author Tomas Karpovic <tomas.karpovic@honestus.lt>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from urllib.request import urlopen
from urllib.parse import urlparse
import lxml.etree as ET
from datetime import datetime
import psycopg2

from odoo import models, fields, _, api

from ..utils import get_errors_string, get_exception_error_string, isfloat


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
    _order = "productBeschrijving, id"

    idArtikel = fields.Char("Article ID RC")
    artikelnummer = fields.Char()
    typenummer = fields.Char("Type Number")
    ean = fields.Char("EAN", readonly=True)
    brand_id = fields.Many2one("import.selected.brands.table", "Brand")
    merk = fields.Char()
    merk_origineel = fields.Char()
    rrp = fields.Float("RRP")
    taksen = fields.Float()
    vkp = fields.Float("Sales Price")
    productTitel = fields.Char()
    productInfo = fields.Html("Product Description")
    productBeschrijving = fields.Char("Product Name")
    idCat_1 = fields.Integer("Product Category Level 1 ID")
    idCat_2 = fields.Integer("Product Category Level 2 ID")
    idCat_3 = fields.Integer("Product Category Level 3 ID")
    cat_1 = fields.Char("Product Category Level 1")
    cat_2 = fields.Char("Product Category Level 2")
    cat_3 = fields.Char("Product Category Level 3")
    URL_afbeelding_1 = fields.Char()
    URL_afbeelding_2 = fields.Char()
    URL_afbeelding_3 = fields.Char()
    URL_afbeelding_4 = fields.Char()
    URL_afbeelding_5 = fields.Char()
    URL_PDF_N = fields.Char()
    URL_LEV_N = fields.Char()
    accessoires = fields.Char()
    status = fields.Integer()
    update_trigger = fields.Datetime(readonly=True)
    product_selected_for_import = fields.Boolean()
    product_is_active = fields.Boolean()

    def _sync_rc_import_product_table(self):
        self.sync_rc_import_product_table()
        # celery = {"countdown": 2}
        # self.env["celery.task"].call_task(
        #     "import.product.table",
        #     "sync_rc_import_product_table",
        #     celery=celery,
        # )

    def _create_edit_products(self):
        self.create_edit_products()
        # celery = {"countdown": 2}
        # self.env["celery.task"].call_task(
        #     "import.product.table",
        #     "create_edit_products",
        #     celery=celery,
        # )

    def create_edit_import_products(
        self,
        products,
        errors,
        processed_products,
    ):
        brand_obj = self.env["import.selected.brands.table"]

        existing_products = self.search([("product_is_active", "=", True)])
        existing_products.write({"product_is_active": False})

        existing_brands = brand_obj.search([("brand_is_active", "=", True)])
        existing_brands.write({"brand_is_active": False})

        empty_ean_count = 0

        for product_el in products:
            ean = product_el.find("EAN")
            update_trigger_text = product_el.find("update_trigger").text
            merk_origineel = product_el.find("merk_origineel").text

            if not ean.text:
                empty_ean_count += 1
                continue

            vals = {
                "idArtikel": product_el.find("idArtikel").text,
                "artikelnummer": product_el.find("artikelnummer").text,
                "typenummer": product_el.find("typenummer").text,
                "ean": ean.text,
                "merk": product_el.find("merk").text,
                "merk_origineel": merk_origineel,
                "productTitel": product_el.find("productTitel").text,
                "productInfo": product_el.find("productInfo").text,
                "productBeschrijving": product_el.find("productBeschrijving").text,
                "idCat_1": product_el.find("idCat_1").text,
                "idCat_2": product_el.find("idCat_2").text,
                "idCat_3": product_el.find("idCat_3").text,
                "cat_1": product_el.find("cat_1").text,
                "cat_2": product_el.find("cat_2").text,
                "cat_3": product_el.find("cat_3").text,
                "URL_afbeelding_1": product_el.find("URL_afbeelding_1").text,
                "URL_afbeelding_2": product_el.find("URL_afbeelding_2").text,
                "URL_afbeelding_3": product_el.find("URL_afbeelding_3").text,
                "URL_afbeelding_4": product_el.find("URL_afbeelding_4").text,
                "URL_afbeelding_5": product_el.find("URL_afbeelding_5").text,
                "URL_PDF_N": product_el.find("URL_PDF_N").text,
                "URL_LEV_N": product_el.find("URL_LEV_N").text,
                "accessoires": product_el.find("accessoires").text,
                "status": product_el.find("status").text,
                "product_is_active": True,
            }

            brand = brand_obj.search([("name", "=", merk_origineel)])
            if not brand:
                brand = brand_obj.create(
                    {"name": merk_origineel, "supplier": "Royal Crown"}
                )
            brand.brand_is_active = True
            vals["brand_id"] = brand.id

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
                product_el.find("RRP").text
                and product_el.find("RRP").text.replace(",", ".")
                or "0.0"
            )
            taksen = (
                product_el.find("taksen").text
                and product_el.find("taksen").text.replace(",", ".")
                or "0.0"
            )
            vkp = (
                product_el.find("VKP").text
                and product_el.find("VKP").text.replace(",", ".")
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

        res = {
            "result": _("Products successfully imported/edited in Odoo."),
            "res_model": "import.product.table",
        }
        if not processed_products:
            res["result"] = _(
                "Products were not imported/edited. "
                "Please check source file location settings."
            )
        if errors:
            res["result"] = _(
                "Some products successfully imported/edited in Odoo.\n"
                "Some have failed:\n{error}"
            ).format(
                error=get_errors_string(errors),
            )
        print(res["result"])
        return res

    def process_create_edit_products(self, processed_products, errors):
        product_tmpl_obj = self.env["product.template"]
        product_image_obj = self.env["product.image"]
        product_public_category_obj = self.env["product.public.category"]
        company = self.env.company
        product_name_field = company.product_name_field_id
        import_product_mappings = company.import_product_mapping_ids
        import_extra_image_mappings = company.import_extra_image_mapping_ids
        import_eshop_categories_mappings = company.import_eshop_category_mapping_ids

        import_products_to_process = self.search(
            [
                ("product_selected_for_import", "=", True),
                ("product_is_active", "=", True),
            ]
        )
        for import_product in import_products_to_process:
            ean = import_product.ean
            try:
                vals = {
                    "name": getattr(import_product, product_name_field.name),
                    "ean": ean,
                    "rc_last_update_date": import_product.update_trigger,
                }
                for mapping in import_product_mappings:
                    vals[mapping.product_template_field_id.name] = getattr(
                        import_product, mapping.import_product_table_field_id.name
                    )

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
                    product_template._onchange_image_url()
                    if not product_template.is_published:
                        product_template.website_publish_button()

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

        res = {
            "result": _(
                "Products successfully created/edited and published in Odoo web shop."
            ),
            "res_model": "import.product.table",
        }
        if not processed_products:
            res["result"] = _(
                "Products were not created/edited. Please check mapping settings."
            )
        if errors:
            res["result"] = _(
                "Some products successfully created/edited "
                "and published in Odoo web shop.\n"
                "Some have failed:\n{error}"
            ).format(
                error=get_errors_string(errors),
            )
        print(res["result"])
        return res
