# -*- coding: utf-8 -*-

from openerp import models, fields


class HRExpense(models.Model):
    _inherit = 'hr.expense.expense'

    attachment_ids = fields.One2many(
        'ir.attachment',
        'expense_id',
        string='Attachment',
        copy=False,
    )
