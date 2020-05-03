from logging import getLogger
from datetime import datetime, date
from time import mktime
from json import loads as json_loads

from requests import get
from bs4 import BeautifulSoup

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
        """Get and parse data from source. If parse is False, then just
        check an availability
        """
        try:
            response = get(f'{self.base_url}{self.path}')
            response.raise_for_status()
            if parse:
                self.models = self.parse_data(response.content)
            return self
        except Exception as e:
            lg.exception(e)
            raise

    def parse_data(self, content):
        """Parsing given content"""
        soup = BeautifulSoup(content, 'lxml')
        model_today, model_total = CovidCase(), CovidTotalCases()
        datestr = soup.find('h1', {"class": "cv-section__title"}).text
        data = json_loads(soup.find('cv-stats-virus').attrs[':stats-data'])
        actual_date = self.__extract_date(datestr)

        model_today.set_actual_date(actual_date)
        model_total.set_actual_date(actual_date)

        model_today.pop(
            self._i(data['sickChange']),
            self._i(data['healedChange']),
            self._i(data['diedChange'])
        )
        model_total.pop(
            self._i(data['sick']),
            self._i(data['healed']),
            self._i(data['died'])
        )

        model_today.set_request_datetime()
        model_total.set_request_datetime()
        model_today.set_region(self.region_name)
        model_total.set_region(self.region_name)

        return model_today.self_validate(), model_total.self_validate()

    def __extract_date(self, datestr):
        """Extract date from given datestr, it works only for the current
        source object
        """
        lg.debug(f'extracting date from {datestr}')
        month_trans = {'январ': 1, 'февр': 2, 'март': 3, 'апрел': 4, 'май': 5,
                       'мая': 5, 'июн': 6, 'июл': 7, 'август': 8, 'сентябр': 9,
                       'октябр': 10, 'ноябр': 11, 'декабр': 12}
        _, _, _, _, _, day, month, _ = datestr.split()
        for m, num in month_trans.items():
            if m in month:
                month = num
                break
        d = date(datetime.utcnow().year, month, int(day))
        return mktime(d.timetuple())

    @staticmethod
    def _i(val):
        """Clean given str val and returns int"""
        # TODO: place to utils
        return int(val.replace('+', '').replace(' ', ''))
