from dotenv import load_dotenv
load_dotenv()

import logging
logging.basicConfig(
    # filename='out.txt',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
log = logging.getLogger()

import os
import schedule
import datetime, time

from telegram import ParseMode, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CallbackContext, CommandHandler, CallbackQueryHandler

from amazon_scraped import AmazonScraped
from dbhelper import DBHelper
from models import *

PORT = os.environ.get("PORT",'80')
TOKEN = os.environ.get("TOKEN",'')
RESULT_COUNT = int(os.environ.get("RESULT_COUNT", "3"))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL","https://amazing-deals-app.herokuapp.com/")

DEPLOY_ENV = os.environ.get("DEPLOY_ENV",'local')

dbhelper = DBHelper()

# start_items = [Item(1, "Top 5 Offers"), Item(2, "Custom (Max 30 results)")]
start_items = [Item(1, "Top 10 Offers")]
user_result_count = 0

def bold(msg):
    return '<b>' + msg + '</b>'

def add_associate_id(url):
    associate_tag = 'onlinesho0a17-21'
    
    breaks = url.split('?',1)
    result_url = breaks[0] + '?tag=' + associate_tag
    if breaks[1] is not None:
        result_url += '&' + breaks[1]
    return result_url

def get_chat_id(update, context):
    chat_id = -1

    if update.message is not None:
        chat_id = update.message.chat.id
    elif update.callback_query is not None:
        chat_id = update.callback_query.message.chat.id
    elif update.poll is not None:
        chat_id = context.bot_data[update.poll.id]

    return chat_id

def add_suggested_actions(update, context, response):
    options = []

    for item in response.items:
        options.append(InlineKeyboardButton(item.message, callback_data=item.id))

    reply_markup = InlineKeyboardMarkup([options])

    # update.message.reply_text(response.message, reply_markup=reply_markup)
    context.bot.send_message(chat_id=get_chat_id(update, context), text=response.message, reply_markup=reply_markup)

def button(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    selected_option = int(query.data)

    selected_option_msg = "Invalid message"

    for item in start_items:
        if item.id == selected_option:
            selected_option_msg = item.message
            break

    query.edit_message_text(text=f"Selected option: {selected_option_msg}")
    log.info("Button CLicked.. Getting Data")

    process(update, context)

def start(update: Update, context: CallbackContext):
    log.info("start START")
    buttons = MultiItems("How would you like to search?", start_items)
    add_suggested_actions(update, context, buttons)

def process(update: Update, context: CallbackContext):
    # context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

    # context.bot.send_message(chat_id, text)

    deals = dbhelper.get_deals_data(10)

    log.info("Sending deals data to telegram START")

    for deal in deals:
        offer_title = bold('GET ' + deal.off_percent + ' OFF')
        title = bold(deal.title)
        deal_price = 'Deal Price= ' + deal.deal_price
        mrp = 'MRP= ' + deal.mrp
        off_percent = bold('Off Percent= ' + deal.off_percent)
        rating = deal.rating
        claim_percent = deal.claim_percent + '% claimed'
        time_end = bold(deal.time_end) + ' after message is posted'
        url = add_associate_id(deal.url)
        last_update = deal.updated
        
        msg = offer_title + "\n\n" + title + "\n" + deal_price + "\n" + mrp + "\n" + off_percent + "\n" + rating + "\n" + claim_percent + "\n" + time_end + "\n\nBUY NOW:\n" + url
        # log.info(msg)
        context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode = ParseMode.HTML)

    log.info("Sending deals data to telegram END")

def scheduled_job():
    log.info(f"Running schedular {datetime.datetime.now()}")

    asd = AmazonScraped()
    deals = asd.get_lightning_deals(50)

    log.info("Sending deals data to DB START")

    dbhelper.delete_deals_table()
    dbhelper.create_deals_table()

    for deal in deals:

        deal_obj = Deal()
        deal_obj.set_deal_data(deal)
        deal_id = dbhelper.insert_deals_data(deal_obj)
    log.info("Sending deals data to DB END")

def start_schedular():
    schedule.every(3).minutes.do(scheduled_job)
    log.info("Deals Schedular started")
    while True:
        schedule.run_pending()
        time.sleep(1)

def main():
    updater = Updater(token=TOKEN, use_context=True, request_kwargs={'read_timeout': 60, 'connect_timeout': 60})
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    
    dispatcher.add_handler(CallbackQueryHandler(button))

    dispatcher.run_async(start_schedular)

    ## Uncomment For local env
    updater_started = True
    if DEPLOY_ENV == 'prod':
        updater.start_webhook(listen="0.0.0.0",
                        port=PORT,
                        url_path=TOKEN,
                        webhook_url=WEBHOOK_URL + TOKEN)
    elif DEPLOY_ENV == 'local':
        updater.start_polling()
    else:
        updater_started = False
    
    if updater_started:
        log.info("Webhook started")
        updater.idle()

    else:
        log.error("Webhook start Failed")

if __name__ == '__main__':

    main()