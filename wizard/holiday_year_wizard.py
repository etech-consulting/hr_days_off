# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil import rrule

from openerp.osv import osv
from openerp.osv import fields
from openerp.tools.translate import _
from openerp.tools.misc import DEFAULT_SERVER_DATE_FORMAT as DT_FORMAT


class holiday_year_wizard(osv.osv):
    _name = 'training.holiday.year.wizard'
    _columns = {
        'year': fields.integer('Year', required=True),
    }
    _defaults = {
        'year': lambda *a: datetime.today().year,
    }

    def action_cancel(self, cr, uid, ids, context=None):
        return {'type': 'ir.actions.act_window_close'}

    def action_apply(self, cr, uid, ids, context=None):
        if not ids:
            return False
        holiday_year_obj = self.pool.get('training.holiday.year')
        holiday_period_obj = self.pool.get('training.holiday.period')
        categ = self.pool.get('training.holidays.category').search(cr, uid, [('name', '=', 'Week-End')])
        if not categ:
            cat = self.pool.get('training.holidays.category').create(cr, uid, {'name': 'Week-End'})
            categ = [cat]
        wizard = self.browse(cr, uid, ids[0], context=context)
        try:
            year_start = datetime.strptime('%04s-01-01' % (wizard.year,), DT_FORMAT)
            year_end = datetime.strptime('%04s-12-31' % (wizard.year,),
                                         DT_FORMAT)
        except:
            raise osv.except_osv(_('Error!'),
                                 _('Please enter valid year'))

        year_id = holiday_year_obj.create(cr, uid, {'year': wizard.year}, context=context)

        # Generate holiday periods for each week-end of requested year
        # NOTE: we use ISO week number, but if the 1st saturday of the
        #       year is before the 1st thursday we force week-num to 0
        year_rule = rrule.rrule(rrule.DAILY, dtstart=year_start, until=year_end, byweekday=(rrule.SA))
        for saturday in year_rule:
            iso_year, iso_weeknum, iso_weekday = saturday.isocalendar()
            weeknum = iso_year == wizard.year and iso_weeknum or 0
            holiday_period_obj.create(cr, uid, {
                'year_id': year_id,
                'date_start': saturday.strftime(DT_FORMAT),
                'date_stop': (saturday+relativedelta(days=1)).strftime(DT_FORMAT),
                'name': _('Week-End %02d') % (weeknum,),
                'categ': categ[0],
            }, context=context),

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'training.holiday.year',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': year_id,
        }

    def action_apply_scheduler(self, cr, uid, context=None):
        holiday_year_obj = self.pool.get('training.holiday.year')
        holiday_period_obj = self.pool.get('training.holiday.period')
        categ = self.pool.get('training.holidays.category').search(cr, uid, [('name', '=', 'Week-End')])
        if not categ:
            cat = self.pool.get('training.holidays.category').create(cr, uid, {'name': 'Week-End'})
            categ = [cat]
        date = datetime.now()
        year = date.strftime("%Y")
        year = int(year)
        year += 1
        try:
            year_start = datetime.strptime('%04s-01-01' % (year,), DT_FORMAT)
            year_end = datetime.strptime('%04s-12-31' % (year,), DT_FORMAT)
        except:
            raise osv.except_osv(_('Error!'),
                                 _('Please enter valid year'))

        year_id = holiday_year_obj.create(cr, uid, {'year': year}, context=context)

        # Generate holiday periods for each week-end of requested year
        # NOTE: we use ISO week number, but if the 1st saturday of the
        #       year is before the 1st thursday we force week-num to 0
        year_rule = rrule.rrule(rrule.DAILY, dtstart=year_start, until=year_end, byweekday=(rrule.SA))
        for saturday in year_rule:
            iso_year, iso_weeknum, iso_weekday = saturday.isocalendar()
            weeknum = iso_year == year and iso_weeknum or 0
            holiday_period_obj.create(cr, uid, {
                'year_id': year_id,
                'date_start': saturday.strftime(DT_FORMAT),
                'date_stop': (saturday+relativedelta(days=1)).strftime(DT_FORMAT),
                'name': _('Week-End %02d') % (weeknum,),
                'categ': categ[0],
            }, context=context),

        return True

holiday_year_wizard()
