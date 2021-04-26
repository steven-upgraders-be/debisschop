# Copyright (C) 2021 Honestus <http://www.honestus.lt>
# @author Tomas Karpovic <tomas.karpovic@honestus.lt>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _


def get_errors_string(errors):
    return _("Error!\n%s") % "\n".join(errors)


def get_exception_error_string(number, e, source="category"):
    case = _("category level:")
    if source == "attribute":
        case = _("attribute file number:")
    if source == "product":
        case = _("products")
    main_string = _("Error in syncing of {case} {number}\n").format(
        case=case,
        number=number,
    )
    if source == "product_template":
        main_string = _("Product import in shop failed:\n")
    return "".join(
        [
            main_string,
            str(e),
            "\n",
        ]
    )


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False
