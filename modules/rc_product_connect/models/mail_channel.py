# Copyright (C) 2021 Honestus <http://www.honestus.lt>
# @author Tomas Karpovic <tomas.karpovic@honestus.lt>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class MailChannel(models.Model):
    _inherit = "mail.channel"

    def post_system_message(self, message):
        poster = self.sudo().env.ref("rc_product_connect.channel_rc_product_connect")
        if not (poster and poster.exists()):
            return False
        try:
            poster.message_post(body=message, subtype_xmlid="mail.mt_comment")
        except Exception:
            pass

    def unlink(self):
        result = super(MailChannel, self).unlink()
        if not self.sudo().env.ref(
            "rc_product_connect.channel_rc_product_connect", raise_if_not_found=False
        ):
            raise UserError(
                _(
                    "You cannot delete this channel, because it is used for logs of "
                    "module RC Product Connect."
                )
            )
        return result
