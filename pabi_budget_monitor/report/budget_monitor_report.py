# -*- coding: utf-8 -*-
from openerp import models
from openerp import tools
from openerp.addons.pabi_chartfield.models.chartfield import \
    CHART_FIELDS, ChartField


class BudgetMonitorReport(ChartField, models.Model):
    _inherit = 'budget.monitor.report'

    def _get_dimension(self):
        # Add dimensions from chart field
        dimensions = super(BudgetMonitorReport, self)._get_dimension()
        for d in dict(CHART_FIELDS).keys():
            dimensions += ', %s' % (d,)
        dimensions += ', chart_view'
        return dimensions

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" %
                   (self._table, self._get_sql_view(),))
