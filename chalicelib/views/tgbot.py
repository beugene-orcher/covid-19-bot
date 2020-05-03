"""
tgbot.py view declares handler for getting, processing and returning Telegram
updates
"""
from logging import getLogger

from chalice import Blueprint

from chalicelib.covid19bot import dispatcher, get_update
from chalicelib.configer import APP_NAME


lg = getLogger(f'{APP_NAME}.{__name__}')
bp = Blueprint(__name__)


@bp.route(f'/handler', methods=['POST'])
def handler():
    """Getting updates from telegram server and processing their"""
    try:
        dispatcher.process_update(get_update(bp.current_request))
    except Exception as e:
        lg.exception(e)
