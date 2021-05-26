# Copyright (C) 2021 Honestus <http://www.honestus.lt>
# @author Tomas Karpovic <tomas.karpovic@honestus.lt>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _


def get_errors_string(errors):
    return _("Error!\n%s") % "\n".join(errors)


def get_exception_error_string(ean, e):
    main_string = ""
    if ean:
        main_string = _(
            "Error while updating stock for product with EAN code: {ean}\n"
        ).format(ean=ean)
    return "".join(
        [
            main_string,
            str(e),
            "\n",
        ]
    )
