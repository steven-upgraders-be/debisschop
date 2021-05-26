# Copyright (C) 2021 Honestus <http://www.honestus.lt>
# @author Tomas Karpovic <tomas.karpovic@honestus.lt>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    ftp_server = fields.Char(related="company_id.ftp_server", readonly=False)
    ftp_username = fields.Char(related="company_id.ftp_username", readonly=False)
    ftp_password = fields.Char(related="company_id.ftp_password", readonly=False)
    filename = fields.Char(related="company_id.filename", readonly=False)
