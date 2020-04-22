from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler

from chalicelib.configer import TG_TOKEN


bot = Bot(token=TG_TOKEN)
dispatcher = Dispatcher(bot, None, use_context=True)


def get_update(request):
    return Update.de_json(request.json_body, bot)


def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('hello eugene!')


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('help eugene!')


def add_handlers(dispatcher):
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))


add_handlers(dispatcher)
