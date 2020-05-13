from logging import getLogger
from datetime import datetime, date
from json import dumps as json_dumps
from decimal import Decimal

from chalicelib.configer import APP_NAME, REGIONS, COVID_TYPE_EVENTS


lg = getLogger(f'{APP_NAME}.{__name__}')

default_actual_date = date.fromtimestamp(0).isoformat().split('T')[0]
default_region = 'unknown'


class BaseModel(object):

    def self_validate(self):
        return self

    def from_dict(self, dict_model):
        for key, val in dict_model.items():
            if isinstance(val, Decimal):
                self.__setattr__(key, int(val))
            else:
                self.__setattr__(key, val)
        return self.self_validate()

    def to_json(self):
        if 'to_dict' in dir(self):
            return json_dumps(self.to_dict())
        else:
            raise ModelException(f"object has no attribute to_dict")

    def __str__(self):
        if 'to_dict' in dir(self):
            return str(self.to_dict())
        else:
            raise ModelException(f"object has no attribute to_dict")


class CovidCase(BaseModel):
    cases = -1
    deaths = -1
    recovered = -1
    actual_date = default_actual_date
    region = default_region
    event = 'EVENT_NEW_CASES'

    def __init__(self, *args, **kwargs):
        self.pop(*args)
        if kwargs.get('event') == 'total':
            self.event = 'EVENT_TOTAL_CASES'
        if kwargs.get('actual_date'):
            self.set_actual_date(kwargs['actual_date'])
        if kwargs.get('region'):
            self.region = kwargs['region']

    def self_validate(self):
        if self.region == default_region:
            raise ModelException(f"region has a default region")
        if self.region not in REGIONS:
            raise ModelException(f"region must be in {REGIONS}")
        if self.event not in COVID_TYPE_EVENTS:
            raise ModelException(f"event has a default value")
        if self.actual_date == default_actual_date:
            raise ModelException(f"actual_date has a default date")
        if self.cases == -1 or self.deaths == -1 or self.recovered == -1:
            raise ModelException(f'values must be positive')
        return self

    def pop(self, *args):
        lg.debug(f'model is populated by args: {args}')
        if args:
            try:
                self.cases, self.recovered, self.deaths = args
                self.set_request_datetime()
            except ValueError as e:
                lg.warn(e)

    def to_dict(self):
        return {
            'region': self.region,
            'actual_date': self.actual_date,
            'cases': self.cases,
            'deaths': self.deaths,
            'recovered': self.recovered,
            'request_datetime': self.request_datetime,
            'event': self.event
        }

    def set_request_datetime(self):
        self.request_datetime = datetime.utcnow().isoformat()

    def set_actual_date(self, dt):
        self.actual_date = datetime.fromtimestamp(dt).isoformat().split('T')[0]

    def set_region(self, region):
        self.region = region


class Subscription(BaseModel):
    chat_id = -1
    region = default_region

    def __init__(self, *args, **kwargs):
        self.pop(*args)

    def self_validate(self):
        if self.region == default_region:
            raise ModelException(f"region has a default value")
        if self.region not in REGIONS:
            raise ModelException(f"region must be in {REGIONS}")
        if self.chat_id == -1:
            raise ModelException(f"chat_id has a default value")
        return self

    def pop(self, *args):
        lg.debug(f'model is populated by args: {args}')
        if args:
            try:
                self.chat_id, self.region = args
            except ValueError as e:
                lg.warn(e)

    def to_dict(self):
        return {'chat_id': self.chat_id, 'region': self.region}


class BotNotification(BaseModel):
    region = default_region
    actual_date = default_actual_date

    def __init__(self, *args, **kwargs):
        self.pop(*args)

    def self_validate(self):
        if self.region == default_region:
            raise ModelException(f"region has a default value")
        if self.region not in REGIONS:
            raise ModelException(f"region must be in {REGIONS}")
        if self.actual_date == default_actual_date:
            raise ModelException(f"actual_date has a default date")
        return self

    def pop(self, *args):
        lg.debug(f'model is populated by args: {args}')
        if args:
            try:
                self.region, self.actual_date = args
            except ValueError as e:
                lg.warn(e)

    def to_dict(self):
        return {'region': self.region, 'actual_date': self.actual_date}


class ModelException(Exception):

    def __init__(self, message):
        super().__init__(message)
