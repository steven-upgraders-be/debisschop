# Copyright (C) 2021 Honestus <http://www.honestus.lt>
# @author Tomas Karpovic <tomas.karpovic@honestus.lt>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "RC Product Connect",
    "summary": """
        Scheduled supplier products data import from XML files.
    """,
    "author": "UAB Honestus",
    "website": "https://www.honestus.lt",
    "category": "Specific Industry Applications",
    "version": "0.1",
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
    ],
}
