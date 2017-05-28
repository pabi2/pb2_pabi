# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
from openerp.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sequence_id = fields.Many2one(
        'ir.sequence',
        string='Asset Sequence',
        help="Each product asset will have a unique running sequence"
    )
    asset_category_id = fields.Many2one(
        'account.asset.category',
        string='Asset Category',
    )

    @api.onchange('asset_category_id')
    def _onchange_asset_category_id(self):
        self.sequence_id = False
        self.categ_id = self.asset_category_id.product_categ_id

    @api.multi
    @api.constrains('asset_category_id', 'categ_id')
    def _check_category(self):
        for rec in self:
            if rec.asset_category_id and \
                    rec.categ_id != rec.asset_category_id.product_categ_id:
                raise ValidationError(
                    _('Internal Category not conform with Asset Category!'))
