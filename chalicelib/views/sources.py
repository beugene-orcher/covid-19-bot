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
from telegram import ParseMode, error as tg_error

from chalicelib.messages import TGCaseStatsMessage
from chalicelib.covid19bot import bot
from chalicelib.models import Subscription, CovidCase, BotNotification
from chalicelib.russia import RussiaOfficialSource
from chalicelib.response import CustomJSONResponse
from chalicelib.ddb_manage import (
    put_case,
    put_subscription,
    get_subscriptions
)
from chalicelib.sns_manage import (
    publish_to_sns,
    SNSManageError
)
from chalicelib.configer import (
    APP_NAME,
    SNS_TOPIC_FOR_COVID_CASES,
    SNS_TOPIC_FOR_SUBSCRIPTIONS,
    SNS_TOPIC_FOR_BOT_NOTIFICATIONS
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
        body['new'] = new_cases.to_dict()
        body['total'] = total_cases.to_dict()
        body['message'], code = 'OK', 200
    except Exception as e:
        body['message'], code = 'Fail while processing data', 500
        lg.exception(getattr(e, 'message', repr(e)))
    finally:
        return CustomJSONResponse(body, code)


# Application API
@bp.schedule(Cron("0/5", "7-18", "?", "*", "*", "*"))
def russia_job_handler(event):
    """Regular job for extracting data from Russia source. Extracted data
    isn't processed there, but publishing to AWS SNS
    """
    lg.info('scheduled russia handler is starting...')
    try:
        for model in RussiaOfficialSource().request().models:
            publish_to_sns(model, SNS_TOPIC_FOR_COVID_CASES)
    except SNSManageError as e:
        lg.warn(getattr(e, 'message', repr(e)))
    except Exception as e:
        lg.exception(getattr(e, 'message', repr(e)))


@bp.on_sns_message(topic=SNS_TOPIC_FOR_COVID_CASES)
def covid_case_handler(event):
    """SNS receiver for processing data SNS event and putting to DynamoDB"""
    lg.info("covid case handler is getting the event...")
    lg.debug(f'sns event is {event}')
    try:
        model_covid = CovidCase().from_dict(json_loads(event.message))
        if put_case(model_covid):
            lg.info(f'new cases are found, publish notification event')
            model_notification = BotNotification(
                model_covid.region,
                model_covid.actual_date
            )
            publish_to_sns(model_notification, SNS_TOPIC_FOR_BOT_NOTIFICATIONS)
        else:
            lg.info(f'no updates of cases')
    except Exception as e:
        lg.exception(getattr(e, 'message', repr(e)))


@bp.on_sns_message(topic=SNS_TOPIC_FOR_SUBSCRIPTIONS)
def subscriptions_handler(event):
    """SNS receiver for accepting subscriptions"""
    lg.info(f"subscriptions handler is getting the event...")
    lg.debug(f'sns event is {event}')
    try:
        put_subscription(
            Subscription().from_dict(json_loads(event.message))
        )
    except Exception as e:
        lg.exception(getattr(e, 'message', repr(e)))


@bp.on_sns_message(topic=SNS_TOPIC_FOR_BOT_NOTIFICATIONS)
def notifications_handler(event):
    """SNS receiver for accepting notifications"""
    lg.info(f'notifications nandler is getting the event')
    lg.debug(f'sns event is {event}')
    try:
        broken_subscriptions = []
        model = BotNotification().from_dict(json_loads(event.message))
        region = model.region
        subscriptions = get_subscriptions(region)
        message = TGCaseStatsMessage(region).get_message()
        for sub in subscriptions:
            try:
                bot.send_message(
                    text=message,
                    chat_id=sub.chat_id,
                    parse_mode=ParseMode.MARKDOWN
                )
            except tg_error.BadRequest:
                # TODO: implement delete subscriptions if 'No chat'
                broken_subscriptions.append(sub)
                pass
    except Exception as e:
        lg.exception(getattr(e, 'message', repr(e)))
