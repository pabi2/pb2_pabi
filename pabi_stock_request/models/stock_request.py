# -*- coding: utf-8 -*-

from openerp import api, models, _
from lxml import etree
from openerp.osv.orm import setup_modifiers


class StockRequest(models.Model):
    _inherit = 'stock.request'

    @api.model
    def fields_view_get(self, view_id=None, view_type=False,
                        toolbar=False, submenu=False):
        # button_confirm_hide = False
        # User = self.env['res.users']
        # user = User.browse(self._uid)
        # user_ou_ids = user.operating_unit_ids._ids
        # if self.operating_unit_id.id not in user_ou_ids:
        #     button_confirm_hide = True
        result = super(StockRequest, self).\
            fields_view_get(view_id=view_id, view_type=view_type,
                            toolbar=toolbar, submenu=submenu)
        # print result['fields']
        # if button_confirm_hide:
        #     doc = etree.XML(result['arch'])
        #
        #     nodes = doc.xpath("//button[@name='action_verify']")
        #     for node in nodes:
        #         node.set('invisible', '1')
                # setup_modifiers(
                #     node, result['buttons'][node.attrib['name']])
        #     nodes = doc.xpath("//button[@name='action_verify']")
        #     for node in nodes:
        #         node.set('invisible', '1')
        #         setup_modifiers(
        #             node, result['buttons'][node.attrib['name']])
        #     nodes = doc.xpath("//button[@name='action_approve']")
        #     for node in nodes:
        #         node.set('invisible', '1')
        #         setup_modifiers(
        #             node, result['buttons'][node.attrib['name']])
        #     nodes = doc.xpath("//button[@name='action_transfer']")
        #     for node in nodes:
        #         node.set('invisible', '1')
        #         setup_modifiers(
        #             node, result['buttons'][node.attrib['name']])
        # result['arch'] = etree.tostring(doc)
        return result