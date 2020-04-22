from logging import getLogger
from datetime import datetime, date
from time import mktime

from requests import get
from lxml import html

from chalicelib.models import CovidCase, CovidTotalCases
from chalicelib.configer import (
    APP_NAME,
    RUSSIA_OFFICIAL_URL
)


lg = getLogger(f'{APP_NAME}.{__name__}')


class RussiaOfficialSource(object):
    region_name = 'russia'

    def __init__(self, *args, **kwargs):
        self.base_url = RUSSIA_OFFICIAL_URL
        self.path = '/'
        self.models = []

    def request(self, parse=True):
        try:
            response = get(f'{self.base_url}{self.path}')
            response.raise_for_status()
            if parse:
                self.models = self.parse_data(
                    html.fromstring(response.content))
            return self
        except Exception as e:
            lg.exception(e)
            raise

    def parse_data(self, tree):
        """
        """
        model_today, model_total = CovidCase(), CovidTotalCases()

        base = '//div[@class="d-map__counter"]'
        date_xpath = '//div[@class="d-map__title"]/h2/span/text()'
        total_xpath = f'{base}/div[@class="d-map__counter-item"]/h3/text()'
        new_xpath = f'{base}/div[@class="d-map__counter-item"]/h3/sup/text()'

        actual_date = self.extract_date(tree.xpath(date_xpath))
        model_today.set_actual_date(actual_date)
        model_total.set_actual_date(actual_date)

        case, recovered, death = tree.xpath(new_xpath)
        model_today.pop(self._i(case), self._i(recovered), self._i(death))
        case, recovered, death = tree.xpath(total_xpath)
        model_total.pop(self._i(case), self._i(recovered), self._i(death))

        model_today.set_request_datetime()
        model_total.set_request_datetime()
        model_today.set_region(self.region_name)
        model_total.set_region(self.region_name)

        return model_today.self_validate(), model_total.self_validate()

    def extract_date(self, datelist):
        month_trans = {'январ': 1, 'февр': 2, 'март': 3, 'апрел': 4, 'май': 5,
                       'мая': 5, 'июн': 6, 'июл': 7, 'август': 8, 'сентябр': 9,
                       'октябр': 10, 'ноябр': 11, 'декабр': 12}
        _, _, _, day, month, _ = datelist[0].split()
        for m, num in month_trans.items():
            if m in month:
                month = num
                break
        d = date(datetime.utcnow().year, month, int(day))
        return mktime(d.timetuple())

    @staticmethod
    def _i(val):
        return int(val.replace('+', '').replace(' ', ''))
