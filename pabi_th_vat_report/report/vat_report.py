# -*- coding: utf-8 -*-
from openerp.osv import osv

import openerp.addons.l10n_th_vat_report.report.vat_report as vat_report


class VatReportParser(vat_report.VatReportParser):
    def __init__(self, cr, uid, name, context):
        super(VatReportParser, self).__init__(cr, uid, name, context=context)

    def _from_for_invoice_tax(self):
        res = super(VatReportParser, self)._from_for_invoice_tax()
        res = res + 'LEFT JOIN res_taxbranch t ON (ait.taxbranch_id = t.id)'
        return res

    def _group_by_for_invoice_tax(self):
        res = super(VatReportParser, self)._group_by_for_invoice_tax()
        res = res + ', t.name'
        return res

    def _select_for_invoice_tax(self):
        res = super(VatReportParser, self)._select_for_invoice_tax()
        res = res + ',t.name as taxbranch'
        return res

    def _from_for_voucher_tax(self):
        res = super(VatReportParser, self)._from_for_voucher_tax()
        res = res + 'LEFT JOIN res_taxbranch t ON (avt.taxbranch_id = t.id)'
        return res

    def _group_by_for_voucher_tax(self):
        res = super(VatReportParser, self)._group_by_for_voucher_tax()
        res = res + ', t.name'
        return res

    def _select_for_voucher_tax(self):
        res = super(VatReportParser, self)._select_for_voucher_tax()
        res = res + ',t.name as taxbranch'
        return res


class VatReportAbstarct(osv.AbstractModel):
    _name = "report.l10n_th_vat_report.report_vat"
    _inherit = "report.abstract_report"
    _template = "l10n_th_vat_report.report_vat"
    _wrapped_report_class = VatReportParser

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: