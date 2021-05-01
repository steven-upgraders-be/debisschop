# Copyright (C) 2021 Honestus <http://www.honestus.lt>
# @author Tomas Karpovic <tomas.karpovic@honestus.lt>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    if not version:
        return
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        # changing model for cron
        cron = env.ref(
            "rc_product_connect.cron_sync_rc_category_attributes",
            raise_if_not_found=False,
        )
        cron.write({"model_id": env.ref("product.model_product_attribute").id})
