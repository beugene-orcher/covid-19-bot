"""
sources.py view declares handlers for grabbing data of covid cases, publishing
data to SNS, receiving from SNS and putting to DynamoDB. The module provides
External API and Application API.
External API is a public HTTP JSON API. Application API is an inner API layer
based on AWS Lambda functions, SNS topic and CloudWatch events.
"""
from logging import getLogger
from json import loads as json_loads

from chalice import Blueprint, Cron

from chalicelib.russia import RussiaOfficialSource
from chalicelib.response import CustomJSONResponse
from chalicelib.ddb_manage import ddb
from chalicelib.sns_manage import publish_covid_cases, SNSManageError
from chalicelib.configer import (
    APP_NAME,
    SNS_TOPIC_FOR_COVID_CASES,
    DDB_CASES_TABLE_NAME,
    DDB_TOTAL_TABLE_NAME
)


lg = getLogger(f'{APP_NAME}.{__name__}')
bp = Blueprint(__name__)


# External API
@bp.route('/', methods=['GET'])
def about():
    """Returns a list of supported sources and info"""
    lg.info('OK')
    return CustomJSONResponse({'message': 'Ok'}, 200)


@bp.route('/russia', methods=['GET'])
def get_russia_source():
    """Returns data from rus source"""
    body = {}
    try:
        # getting models from source
        new_cases, total_cases = RussiaOfficialSource().request().models
        # preparing HTTP response
        body.update(new_cases.to_dict())
        body.update(total_cases.to_dict())
        body['message'], code = 'OK', 200
    except Exception as e:
        body['message'], code = 'Fail while processing data', 500
        lg.exception(getattr(e, 'message', repr(e)))
    finally:
        return CustomJSONResponse(body, code)


# Application API
@bp.schedule(Cron("0/5", "7-8", "?", "*", "*", "*"))
def russia_job_handler(event):
    """Regular job for extracting data from Russia source. Extracted data
    isn't processed there, but publishing to AWS SNS
    """
    try:
        new_cases, total_cases = RussiaOfficialSource().request().models
        publish_covid_cases(new_cases)
        publish_covid_cases(total_cases)
    except SNSManageError as e:
        lg.warn(getattr(e, 'message', repr(e)))
    except Exception as e:
        lg.exception(getattr(e, 'message', repr(e)))


@bp.on_sns_message(topic=SNS_TOPIC_FOR_COVID_CASES)
def covid_case_handler(event):
    """SNS receiver for processing data from AWS SNS and putting to DynamoDB"""
    try:
        lg.debug(f'sns event is {event}')
        message = json_loads(event.message)
        if message.get('case'):
            table, item = DDB_CASES_TABLE_NAME, message['case']
        if message.get('total'):
            table, item = DDB_TOTAL_TABLE_NAME, message['total']
        result = ddb.resource.Table(table).put_item(Item=item)
        lg.debug(f'dynamo db result is {result}')
    except Exception as e:
        lg.exception(getattr(e, 'message', repr(e)))
