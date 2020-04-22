"""
"""
from logging import getLogger
from time import sleep
from json import loads as json_loads

from chalice import Chalice

from chalicelib.russia import RussiaOfficialSource
from chalicelib.covid19bot import bot, dispatcher, get_update
from chalicelib.utils import get_base_url
from chalicelib.configer import (
    APP_NAME,
    DEBUG,
    SNS_TOPIC_FOR_COVID_CASES,
    DDB_CASES_TABLE_NAME
)
from chalicelib.aws import (
    create_config_table,
    create_cases_table,
    create_sns_topic,
    get_sns_arn,
    get_sns,
    get_ddb
)


lg = getLogger(f'{APP_NAME}.{__name__}')
app = Chalice(app_name=APP_NAME, debug=DEBUG)


# Application routes
@app.route(f'/handler', methods=['POST'])
def handler():
    try:
        dispatcher.process_update(get_update(app.current_request))
    except Exception as e:
        lg.exception(e)
        return {"status_code": 500}
    return {"status_code": 200}


@app.route('/source/russia/update', methods=['POST'])
def update_russia_source():
    try:
        source = RussiaOfficialSource()
        models = source.request().models
        publisher = get_sns()
        publisher.publish(
            TopicArn=get_sns_arn(),
            Message=str(models[0].to_json())
        )
    except Exception as e:
        lg.exception(e)
        return {"status_code": 500,
                "message": "parsing russia source fail"}


@app.on_sns_message(topic=SNS_TOPIC_FOR_COVID_CASES)
def covid_case_handler(event):
    try:
        message = json_loads(event.message)
        ddb = get_ddb()
        ddb.put_item(Item=message, Table=DDB_CASES_TABLE_NAME)
        return {"status_code": 200,
                "message": "setting webhook success"}
    except Exception as e:
        lg.exception(e)
        return {"status_code": 500,
                "message": "parsing russia source fail"}


# Management routes
# TODO: replace to blueprint
@app.route('/', methods=['GET'])
def hello():
    lg.info('OK')
    return {"message": "OK"}


@app.route('/webhook', methods=['POST'])
def set_webhook():
    try:
        url = get_base_url(app.current_request)
        lg.debug(f'Base URL is {url}')
        bot.setWebhook(f'{url}/handler')
        return {"status_code": 200,
                "message": "setting webhook success"}
    except Exception as e:
        lg.exception(e)
        return {"status_code": 500,
                "message": "setting webhook fail"}


@app.route('/aws/sns', methods=['POST'])
def create_sns_objects():
    try:
        create_sns_topic()
        return {"status_code": 200,
                "message": "creatig sns objects success"}
    except Exception as e:
        lg.exception(e)
        return {"status_code": 500,
                "message": "creating sns objects fail"}


@app.route('/aws/dynamodb', methods=['POST'])
def create_ddb_objects():
    try:
        create_config_table()
        sleep(3)
        create_cases_table()
        return {"status_code": 200,
                "message": "creating dynamodb objects success"}
    except Exception as e:
        lg.exception(e)
        return {"status_code": 500,
                "message": "creating dynamodb objects fail"}
