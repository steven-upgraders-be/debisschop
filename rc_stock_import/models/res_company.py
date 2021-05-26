# Copyright (C) 2021 Honestus <http://www.honestus.lt>
# @author Tomas Karpovic <tomas.karpovic@honestus.lt>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    ftp_server = fields.Char("FTP Server")
    ftp_username = fields.Char("FTP Username")
    ftp_password = fields.Char("FTP Password")
    filename = fields.Char()
