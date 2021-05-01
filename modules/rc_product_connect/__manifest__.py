# Copyright (C) 2021 Honestus <http://www.honestus.lt>
# @author Tomas Karpovic <tomas.karpovic@honestus.lt>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "RC Product Connect",
    "summary": """
        Scheduled supplier products data import from XML files.
    """,
    "author": "Upgraders",
    "website": "https://www.upgraders.be",
    "category": "Specific Industry Applications",
    "version": "0.2",
    "depends": [
        "product",
        "website_sale",
        # "celery",
        "mass_editing",
    ],
    "data": [
        "data/mass_editing_data.xml",
        "data/cron_data.xml",
        "data/ir_module_category_data.xml",
        "security/rc_product_connect_security.xml",
        "security/ir.model.access.csv",
        "views/product_views.xml",
        "views/res_config_settings_views.xml",
        "views/import_product_table_views.xml",
        "views/import_selected_brands_table_views.xml",
        "views/import_product_mapping_views.xml",
        "views/product_category_pims_views.xml",
        "views/product_category_attribute_pims_views.xml",
        "views/import_extra_image_mapping_views.xml",
        "views/import_eshop_category_mapping_views.xml",
    ],
}
