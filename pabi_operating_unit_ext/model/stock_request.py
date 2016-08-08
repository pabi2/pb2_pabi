# -*- coding: utf-8 -*-
from openerp import fields, models, api


class StockRequest(models.Model):
    _inherit = 'stock.request'

    operating_unit_id = fields.Many2one(
        required=True,
        # domain=lambda self: self.env['operating.unit']._ou_domain(),
    )

    @api.model
    def _prepare_inv(self, expense):
        res = super(HrExpenseExpense, self)._prepare_inv(expense)
        res.update({'operating_unit_id': expense.operating_unit_id.id})
        return res