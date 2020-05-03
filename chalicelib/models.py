from logging import getLogger
from datetime import datetime, date
from json import dumps as json_dumps

from chalicelib.configer import APP_NAME


lg = getLogger(f'{APP_NAME}.{__name__}')


class BaseCovidModel(object):
    __default_actual_date = date.fromtimestamp(0).isoformat().split('T')[0]
    actual_date = __default_actual_date
    __default_region = 'unknown'
    region = __default_region

    def self_validate(self):
        for attr, val in self.__dict__.items():
            if attr == 'actual_date' and val == self.__default_actual_date:
                raise ModelException(f"{attr} has a default date")
            if val == -1:
                raise ModelException(f'{attr} must be positive')
            if attr == 'region' and val == self.__default_region:
                raise ModelException(f"{attr} has a default region")
        return self

    def to_json(self):
        if 'to_dict' in dir(self):
            return json_dumps(self.to_dict())
        else:
            raise ModelException(f"object has no attribute to_dict")

    def set_request_datetime(self):
        self.request_datetime = datetime.utcnow().isoformat()

    def set_actual_date(self, dt):
        self.actual_date = datetime.fromtimestamp(dt).isoformat().split('T')[0]

    def set_region(self, region):
        self.region = region

    def __str__(self):
        if 'to_dict' in dir(self):
            return str(self.to_dict())
        else:
            raise ModelException(f"object has no attribute to_dict")


class CovidCase(BaseCovidModel):
    case_new = -1
    death_new = -1
    recovered_new = -1

    def __init__(self, *args, **kwargs):
        self.pop(*args, **kwargs)

    def pop(self, *args, **kwargs):
        if args:
            try:
                lg.debug(f'covid case model is populated by {args}')
                self.case_new, self.recovered_new, self.death_new = args
            except ValueError as e:
                lg.warn(e)

    def to_dict(self):
        return {
            'case': {
                'region': self.region,
                'actual_date': self.actual_date,
                'case_new': self.case_new,
                'death_new': self.death_new,
                'recovered_new': self.recovered_new,
                'request_datetime': self.request_datetime
            }
        }


class CovidTotalCases(BaseCovidModel):
    case_total = -1
    death_total = -1
    recovered_total = -1

    def __init__(self, *args, **kwargs):
        self.pop(*args, **kwargs)

    def pop(self, *args, **kwargs):
        if args:
            try:
                lg.debug(f'covid total cases model is populated by {args}')
                self.case_total, self.recovered_total, self.death_total = args
            except ValueError as e:
                lg.warn(e)

    def to_dict(self):
        return {
            'total': {
                'region': self.region,
                'actual_date': self.actual_date,
                'case_total': self.case_total,
                'death_total': self.death_total,
                'recovered_total': self.recovered_total,
                'request_datetime': self.request_datetime
            }
        }


class ModelException(Exception):

    def __init__(self, message):
        super().__init__(message)
