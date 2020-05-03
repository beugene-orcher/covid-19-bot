from logging import getLogger

from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler
from telegram import ParseMode

from chalicelib.ddb_manage import (
    get_last_record_by_region,
    DDBUnknownRegion,
    DDBNoCases
)
from chalicelib.configer import (
    APP_NAME,
    TG_TOKEN,
    DDB_TOTAL_TABLE_NAME,
    DDB_CASES_TABLE_NAME
)


lg = getLogger(f'{APP_NAME}.{__name__}')
bot = Bot(token=TG_TOKEN)
dispatcher = Dispatcher(bot, None, use_context=True)


def get_update(request):
    """Returns json updates"""
    return Update.de_json(request.json_body, bot)


def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('hello eugene!')


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text(
        'Hello! I can provide statistics about COVID-19 by regions.\n'
        'Commands:\n'
        '/russia - COVID-19 statistics Russia'
    )


def russia(update, context):
    """Send rus stats"""
    # TODO: replace to template class
    lg.info('Russia handler is calling...')
    template = f'**Russia: Covid Statistics**\n\n'
    total_header = f'*Total cases*\n'
    new_header = f'*New cases*\n'
    try:
        total = get_last_record_by_region('russia', DDB_TOTAL_TABLE_NAME)
        lg.debug(f'Total is {total}')
        tot_msg = f'On *{total["actual_date"]}*\n' \
                  f'   __Total cases__: {total["case_total"]:,}\n' \
                  f'   __Recovered__: {total["recovered_total"]:,}\n' \
                  f'   __Left__: {total["death_total"]:,}\n\n'
    except (DDBUnknownRegion, DDBNoCases) as e:
        tot_msg = f'{getattr(e, "message", repr(e))}\n'
    except Exception:
        tot_msg = 'Internal error, try again later, please\n'
    try:
        new = get_last_record_by_region('russia', DDB_CASES_TABLE_NAME)
        lg.debug(f'New is {new}')
        new_msg = f'On *{new["actual_date"]}*\n' \
                  f'   __New cases__: {new["case_new"]:,}\n' \
                  f'   __New recovered__: {new["recovered_new"]:,}\n' \
                  f'   __Left__: {new["death_new"]:,}'
    except (DDBUnknownRegion, DDBNoCases) as e:
        new_msg = f'{getattr(e, "message", repr(e))}\n'
    except Exception:
        new_msg = 'Internal error, try again later, please\n'
    message = template + total_header + tot_msg + new_header + new_msg
    lg.debug(f'Output message is {message}')
    update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)


def add_handlers(dispatcher):
    """Declares telegram handlers"""
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("russia", russia))


add_handlers(dispatcher)
