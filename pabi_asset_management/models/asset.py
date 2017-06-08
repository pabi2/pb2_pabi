# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp import tools
from openerp.modules.module import get_module_resource
from openerp.exceptions import ValidationError
from openerp.addons.pabi_chartfield.models.chartfield \
    import ChartFieldAction


class AccountAssetAsset(ChartFieldAction, models.Model):
    _inherit = 'account.asset.asset'
    # _inherit = ['mail.thread', 'account.asset.asset']

    type = fields.Selection(
        # Need this way of doing default, because default_type in context will
        # cause problem compute depreciation table, it set line type wrongly
        default=lambda self: self._context.get('type') or 'normal',
    )
    code = fields.Char(
        string='Code',  # Rename
        default='/',
    )
    code2 = fields.Char(
        string='Code (legacy)',
        help="Code in Legacy System",
    )
    product_id = fields.Many2one(
        'product.product',
        string='Asset Type',
        domain=[('asset_category_id', '!=', False)],
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="This asset is created from this product class",
    )
    move_id = fields.Many2one(
        'stock.move',
        string='Move',
        readonly=True,
    )
    picking_id = fields.Many2one(
        'stock.picking',
        string='Picking',
        related='move_id.picking_id',
        store=True,
        readonly=True,
    )
    date_picking = fields.Datetime(
        string='Picking Date',
        related='move_id.picking_id.date_done',
        readonly=True,
    )
    purchase_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order',
        related='move_id.purchase_line_id.order_id',
        store=True,
        readonly=True,
    )
    uom_id = fields.Many2one(
        'product.uom',
        string='Unit of Measure',
        related='move_id.product_uom',
        store=True,
        readonly=True,
    )
    no_depreciation = fields.Boolean(
        string='No Depreciation',
        related='category_id.no_depreciation',
        readonly=True,
    )
    # Additional Info
    pr_requester_id = fields.Many2one(
        'res.users',
        string='Requester',
        related='move_id.purchase_line_id.requisition_line_id.'
        'purchase_request_lines.request_id.requested_by',
        # TODO: will change to move_id.purchase_line_id.quo_line_id.req...
        # as issue 1504 is ready
        help="PR Requester of this asset",
    )
    date_issue = fields.Date(
        string='Date Issues',
        readonly=True,
        help="Asset issued date by issue document",
    )
    doc_issue_id = fields.Many2one(
        'account.asset.issue',
        string='Issue Document',
        readonly=True,
    )
    responsible_user_id = fields.Many2one(
        'res.users',
        string='Responsible Person',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    owner_project_id = fields.Many2one(
        'res.project',
        string='Project',
        readonly=True,
        help="Owner project of the budget structure",
    )
    owner_section_id = fields.Many2one(
        'res.section',
        string='Section',
        readonly=True,
        help="Owner section of the budget structure",
    )
    purchase_value = fields.Float(
        default=0.0,  # to avoid false
    )
    requester_id = fields.Many2one(
        'res.users',
        string='Requester',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    location_id = fields.Many2one(
        'stock.location',
        string='Building',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    room = fields.Char(
        string='Room',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    serial_number = fields.Char(
        string='Serial Number',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    warranty_start_date = fields.Date(
        string='Warranty Start Date',
        default=lambda self: fields.Date.context_today(self),
        track_visibility='onchange',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    warranty_expire_date = fields.Date(
        string='Warranty Expire Date',
        default=lambda self: fields.Date.context_today(self),
        track_visibility='onchange',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    # Purchase Method
    pr_purchase_method_id = fields.Many2one(
        'purchase.method',
        string='Purchase Method',
        # TODO: This should be a compute field back to PR
    )
    # Transfer Asset
    target_asset_id = fields.Many2one(
        'account.asset.asset',
        string='Transferred to Asset',
        help="In case of transfer, this field show asset created by this one",
    )
    source_asset_count = fields.Integer(
        string='Source Asset Count',
        compute='_compute_source_asset_count',
    )
    source_asset_ids = fields.One2many(
        'account.asset.asset',
        'target_asset_id',
        string='Source Assets',
        help="List of source asset that has been transfer to this one",
    )
    issued = fields.Boolean(
        string='Issued',
        default=False,
        help="True, if has been issued by account.asset.issue",
    )
    image = fields.Binary(
        string='Image',
    )
    repair_note_ids = fields.One2many(
        'asset.repair.note',
        'asset_id',
        string='Repair Notes',
    )
    depreciation_summary_ids = fields.One2many(
        'account.asset.depreciation.summary',
        'asset_id',
        string='Depreciation Summary',
        readonly=True,
    )
    _sql_constraints = [('code_uniq', 'unique(code)',
                         'Asset Code must be unique!')]

    @api.multi
    def open_source_asset(self):
        self.ensure_one()
        action = self.env.ref('account_asset_management.'
                              'action_account_asset_asset_form')
        result = action.read()[0]
        assets = self.with_context(active_test=False).\
            search([('target_asset_id', '=', self.id)])
        dom = [('id', 'in', assets.ids)]
        result.update({'domain': dom, 'context': {'active_test': False}})
        return result

    @api.multi
    @api.depends()
    def _compute_source_asset_count(self):
        for asset in self:
            _ids = self.with_context(active_test=False).\
                search([('target_asset_id', '=', asset.id)])._ids
            asset.source_asset_count = len(_ids)

    @api.model
    def create(self, vals):
        if vals.get('code', '/') == '/':
            sequence = False
            product_id = vals.get('product_id', False)
            if product_id:
                product = self.env['product.product'].browse(product_id)
                sequence = product.sequence_id
                if not sequence:
                    raise ValidationError(
                        _('No asset sequence setup for selected product!'))
                vals['code'] = self.env['ir.sequence'].next_by_id(sequence.id)
        asset = super(AccountAssetAsset, self).create(vals)
        asset.update_related_dimension(vals)
        # Init Salvage Value from Category
        if self._context.get('create_asset_from_move_line', False):
            if not asset.category_id.no_depreciation:
                asset.salvage_value = asset.category_id.salvage_value
        return asset

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            if record.code and record.code != '/':
                name = "[%s] %s" % (record.code, record.name)
            else:
                name = record.name
            res.append((record.id, name))
        return res

    @api.multi
    def compute_depreciation_board(self):
        assets = self.filtered(lambda l: not l.no_depreciation)
        return super(AccountAssetAsset, assets).compute_depreciation_board()

    @api.multi
    def onchange_category_id(self, category_id):
        res = super(AccountAssetAsset, self).onchange_category_id(category_id)
        asset_category = self.env['account.asset.category'].browse(category_id)
        if asset_category and not asset_category.no_depreciation:
            res['value']['salvage_value'] = asset_category.salvage_value
        return res


class AccountAssetCategory(models.Model):
    _inherit = 'account.asset.category'

    product_categ_id = fields.Many2one(
        'product.category',
        string='Product Category',
        ondelete='restrict',
        required=True,
        help="Grouping of this asset category",
    )
    account_asset_id = fields.Many2one(
        domain=[('type', '=', 'other'), ('user_type.for_asset', '=', True)],
    )
    no_depreciation = fields.Boolean(
        string='No Depreciation',
        default=False,
    )
    salvage_value = fields.Float(
        string='Salvage Value',
        default=0.0,
        help="Default salvage value used when create asset from move line",
    )

    @api.multi
    def write(self, vals):
        res = super(AccountAssetCategory, self).write(vals)
        if 'product_categ_id' in vals:
            Product = self.env['product.product']
            for asset_categ in self:
                products = Product.search([
                    ('asset', '=', True),
                    ('asset_category_id', '=', asset_categ.id)])
                products.write({'categ_id': asset_categ.product_categ_id.id})
        return res


class AccountAssetDepreciationLine(models.Model):
    _inherit = 'account.asset.depreciation.line'

    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscalyear',
        compute='_compute_fiscalyear_id',
        store=True,
    )

    @api.multi
    @api.depends('line_date')
    def _compute_fiscalyear_id(self):
        Fiscal = self.env['account.fiscalyear']
        for rec in self:
            rec.fiscalyear_id = Fiscal.find(dt=rec.line_date)

    def _setup_move_line_data(self, depreciation_line, depreciation_date,
                              period_id, account_id, type, move_id, context):
        move_line_data = super(AccountAssetDepreciationLine, self).\
            _setup_move_line_data(depreciation_line, depreciation_date,
                                  period_id, account_id, type,
                                  move_id, context)
        asset = depreciation_line.asset_id
        move_line_data.update({'section_id': asset.owner_section_id.id,
                               'project_id': asset.owner_project_id.id})
        return move_line_data


class AssetRepairNote(models.Model):
    _name = 'asset.repair.note'

    asset_id = fields.Many2one(
        'account.asset.asset',
        string='Asset',
        ondelete='cascade',
        index=True,
    )
    date = fields.Date(
        string='Date',
        default=lambda self: fields.Date.context_today(self),
    )
    note = fields.Text(
        string='Note',
    )


class AccountAssetDepreciationSummary(models.Model):
    _name = 'account.asset.depreciation.summary'
    _auto = False
    _rec_name = 'fiscalyear_id'
    _description = 'Fiscal Year depreciation summary of asset'
    _order = 'fiscalyear_id'

    asset_id = fields.Many2one(
        'account.asset.asset',
        string='Asset',
        readonly=True,
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='fiscalyear',
        readonly=True,
    )
    amount_depreciate = fields.Float(
        string='Depreciation Amount',
        readonly=True,
    )

    def init(self, cr):

        _sql = """
            select min(id) as id, asset_id, fiscalyear_id,
            sum(amount) as amount_depreciate
            from account_asset_depreciation_line a
            where type = 'depreciate' and fiscalyear_id is not null
            group by asset_id, fiscalyear_id
        """

        tools.drop_view_if_exists(cr, self._table)
        cr.execute(
            """CREATE or REPLACE VIEW %s as (%s)""" %
            (self._table, _sql,))