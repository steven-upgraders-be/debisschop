# Copyright (C) 2021 Honestus <http://www.honestus.lt>
# @author Tomas Karpovic <tomas.karpovic@honestus.lt>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "RC Stock Import",
    "summary": """
        Scheduled stock data import from XLSX files.
    """,
    "author": "Upgraders",
    "website": "https://www.upgraders.be",
    "category": "Specific Industry Applications",
    "version": "0.1",
    "depends": [
        "rc_product_connect",
    ],
    "data": [
        "data/cron_data.xml",
        "views/res_config_settings_views.xml",
    ],
}
