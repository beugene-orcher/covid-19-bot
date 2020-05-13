from logging import getLogger

from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler
from telegram import ParseMode

from chalicelib.sns_manage import publish_to_sns
from chalicelib.models import Subscription
from chalicelib.messages import (
    TGCaseStatsMessage,
    TGHelpMessage,
    TGSubscribeMessage
)
from chalicelib.configer import (
    APP_NAME,
    TG_TOKEN,
    SNS_TOPIC_FOR_SUBSCRIPTIONS
)


lg = getLogger(f'{APP_NAME}.{__name__}')
bot = Bot(token=TG_TOKEN)
dispatcher = Dispatcher(bot, None, use_context=True)


def get_update(request):
    """Returns json updates"""
    return Update.de_json(request.json_body, bot)


def start(update, context):
    """Send a message when the command /start is issued."""
    message = 'Hello! I can provide you COVID-19 statistics by a country'
    update.message.reply_text(
        message,
        parse_mode=ParseMode.MARKDOWN
    )


def help(update, context):
    """Send a message when the command /help"""
    message = TGHelpMessage().get_message()
    update.message.reply_text(
        message,
        parse_mode=ParseMode.MARKDOWN
    )


def subscribe(update, context):
    """Mock to subscribe command"""
    message = 'You must specify a country to get a subscription. Example: ' \
        '/subscribe\\_russia'
    update.message.reply_text(
        message,
        parse_mode=ParseMode.MARKDOWN
    )


def subscribe_russia(update, context):
    """Get Russia stats subscription"""
    region, chat_id = 'russia', update['message']['chat']['id']
    publish_to_sns(Subscription(chat_id, region), SNS_TOPIC_FOR_SUBSCRIPTIONS)
    message = TGSubscribeMessage(region).get_message()
    update.message.reply_text(
        message,
        parse_mode=ParseMode.MARKDOWN
    )


def unsubscribe_russia(update, context):
    """Delete Russia subscription"""
    update.message.reply_text(
        "It'll be implemented soon",
        parse_mode=ParseMode.MARKDOWN
    )


def unsubscribe_all(update, context):
    """Delete all subscriptions"""
    update.message.reply_text(
        "It'll be implemented soon",
        parse_mode=ParseMode.MARKDOWN
    )


def russia(update, context):
    """Send Russia stats"""
    lg.info('Russia handler is calling...')
    message = TGCaseStatsMessage('russia').get_message()
    lg.debug(f'Output message is {message}')
    update.message.reply_text(
        message,
        parse_mode=ParseMode.MARKDOWN
    )


def add_handlers(dispatcher):
    """Declares telegram handlers"""
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("russia", russia))
    dispatcher.add_handler(CommandHandler("subscribe", subscribe))
    dispatcher.add_handler(CommandHandler(
        "subscribe_russia", subscribe_russia))
    dispatcher.add_handler(CommandHandler(
        "unsubscribe_russia", unsubscribe_russia))
    dispatcher.add_handler(CommandHandler(
        "unsubscribe_all", unsubscribe_all))


add_handlers(dispatcher)
