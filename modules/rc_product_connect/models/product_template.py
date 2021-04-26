# Copyright (C) 2021 Honestus <http://www.honestus.lt>
# @author Tomas Karpovic <tomas.karpovic@honestus.lt>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import requests
import base64

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    ean = fields.Char("EAN", readonly=True)
    rc_last_update_date = fields.Datetime("RC Last Update Date", readonly=True)
    image_url = fields.Char(string="Image URL")

    @api.onchange("image_url")
    def _onchange_image_url(self):
        image = False
        if self.image_url:
            image = base64.b64encode(requests.get(self.image_url).content)
        self.image_1920 = image
