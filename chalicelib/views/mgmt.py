"""
mgmt.py view declares an operation API for inner usage only. It'll be covered
by auth.
"""
from logging import getLogger

from chalice import Blueprint

from chalicelib.response import CustomJSONResponse
from chalicelib.utils import get_base_url
from chalicelib.covid19bot import bot
from chalicelib.configer import APP_NAME


lg = getLogger(f'{APP_NAME}.{__name__}')
bp = Blueprint(__name__)


@bp.route('/', methods=['GET'])
def about():
    """Health checker"""
    lg.info('Health check is OK')
    return CustomJSONResponse({'message': 'Ok'}, 200)


@bp.route('/webhook', methods=['POST'])
def set_webhook():
    """Setting webhook of Telegram bot. Telegram token must be provided
    before a call
    """
    body = {}
    try:
        url = get_base_url(bp.current_request)
        lg.debug(f'Base URL is {url}')
        bot.setWebhook(f'{url}/tgbot/handler')
        body['message'], code = 'OK', 200
    except Exception as e:
        body['message'], code = 'Fail while setting webhook', 500
        lg.exception(getattr(e, 'message', repr(e)))
    finally:
        return CustomJSONResponse(body, code)
