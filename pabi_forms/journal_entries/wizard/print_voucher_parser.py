# -*- encoding: utf-8 -*-
from openerp.addons import jasper_reports
from print_voucher_wizard import *


def print_voucher_parser(cr, uid, ids, data, context):
    return {
        'ids': data['parameters']['ids'],
    }

jasper_reports.report_jasper(
    'report.invoice.voucher',  # report_name in report_data.xml
    'account.move',  # Model View name
    parser=print_voucher_parser
)
