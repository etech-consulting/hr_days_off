# -*- coding: utf-8 -*-
import time
from openerp import models, api, fields, _
from openerp.exceptions import ValidationError
from openerp.tools.misc import DEFAULT_SERVER_DATE_FORMAT as DT_FORMAT


class holiday_period(models.Model):
    _name = 'training.holiday.period'

    year_id = fields.Many2one('training.holiday.year', 'Year', required=True,
                              ondelete='cascade')
    name = fields.Char('Name', size=64, required=True)
    date_start = fields.Date('Date Start', required=True,
                             default=lambda *a: time.strftime(DT_FORMAT))
    date_stop = fields.Date('Date Stop', required=True,
                            default=lambda *a: time.strftime(DT_FORMAT))
    active = fields.Boolean('Active', default=lambda *a: 1)
    categ = fields.Many2one('training.holidays.category', 'Category')

    @api.one
    @api.constrains('date_start', 'date_stop')
    def _check_date_start_stop(self):
        if self.date_start > self.date_stop:
            raise ValidationError(_('Please, check the start date !'))
        return True

    @api.cr
    def is_in_period(self, date):
        if not date:
            raise ValueError(_('''no date specified for
                               'is in period' holiday period check'''))
        cr = self._cr
        cr.execute("SELECT count(id) "
                   "FROM training_holiday_period "
                   "WHERE %s BETWEEN date_start AND date_stop AND active='1'",
                   (date,))
        return cr.fetchone()[0] > 0
