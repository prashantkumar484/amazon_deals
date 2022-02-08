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
import requests

from telegram import ParseMode, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CallbackContext, CommandHandler, CallbackQueryHandler

from amazon_scraped import AmazonScraped
from dbhelper import DBHelper
from models import *

PORT = os.environ.get("PORT",'80')
TOKEN = os.environ.get("TOKEN",'')

MAX_ITEMS = int(os.environ.get("MAX_ITEMS", "200"))
RESULT_COUNT = int(os.environ.get("RESULT_COUNT", "5"))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL","https://amazing-deals-app.herokuapp.com/")

DEPLOY_ENV = os.environ.get("DEPLOY_ENV",'local')

dbhelper = DBHelper()

# start_items = [Item(1, "Top 5 Offers"), Item(2, "Custom (Max 30 results)")]
start_items = [Item("top", "Top Offers")]
next_items = [Item("top", "Top Offers"),Item("prev", "Previous Offers"), Item("next", "Next Offers"), Item("cancel", "Cancel")]
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

def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu

def add_suggested_actions(update, context, response):
    options = []

    for item in response.items:
        options.append(InlineKeyboardButton(item.message, callback_data=item.id))

    # reply_markup = InlineKeyboardMarkup([options])
    reply_markup = InlineKeyboardMarkup(build_menu(options, n_cols=2))

    # update.message.reply_text(response.message, reply_markup=reply_markup)
    context.bot.send_message(chat_id=get_chat_id(update, context), text=response.message, reply_markup=reply_markup)

def button(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    chat_id = get_chat_id(update, context)

    log.info("Button CLicked.. Getting Data")

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    selected_option = query.data

    selected_option_msg = "Invalid message"
    selected_item = [x for x in start_items if x.id==selected_option]
    if len(selected_item)>0:
        selected_item = selected_item[0]
        selected_option_msg = selected_item.message
        query.edit_message_text(text=f"Selected option: {selected_option_msg}")
        process(update, context)
        return
    
    selected_item = [x for x in next_items if x.id==selected_option]
    if len(selected_item)>0:
        selected_item = selected_item[0]
        selected_option_msg = selected_item.message
        query.edit_message_text(text=f"Selected option: {selected_option_msg}")
        curr_offset = 0
        if selected_option=='prev':
            search_history = dbhelper.get_search_history(chat_id)
            curr_offset = search_history[0][1]
            curr_offset = max(curr_offset-RESULT_COUNT, 0)
        elif selected_option=='next':
            search_history = dbhelper.get_search_history(chat_id)
            curr_offset = search_history[0][1]
            curr_offset = min(curr_offset+RESULT_COUNT, MAX_ITEMS-RESULT_COUNT)
        elif selected_option=='top':
            curr_offset=0
        else:
            return
        dbhelper.insert_or_update_search_history(chat_id, curr_offset)
        process(update, context)
        return
    
    

def next_prev_handler(update: Update, context: CallbackContext):
    log.info(f'next_prev_handler start')
    buttons = MultiItems("How would you like to search?", next_items)
    add_suggested_actions(update, context, buttons)

def start(update: Update, context: CallbackContext):
    log.info("start START")
    chat_id = get_chat_id(update, context)
    
    dbhelper.insert_or_update_search_history(chat_id, 0)

    buttons = MultiItems("How would you like to search?", start_items)
    add_suggested_actions(update, context, buttons)

def process(update: Update, context: CallbackContext):
    # context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

    # context.bot.send_message(chat_id, text)

    chat_id = get_chat_id(update,context)
    log.info(f'chat_id= {chat_id}')

    search_history = dbhelper.get_search_history(chat_id)
    offset = search_history[0][1]

    deals = dbhelper.get_deals_data(RESULT_COUNT, offset)

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

        context.bot.send_message(chat_id=chat_id, text=msg, parse_mode = ParseMode.HTML)
    # dbhelper.insert_or_update_search_history(chat_id, offset + RESULT_COUNT)
    log.info("Sending deals data to telegram END")

    next_prev_handler(update,context)

def keep_awake():
    keep_awake_url = 'https://amazing-deals-app.herokuapp.com'
    res = requests.post(keep_awake_url)
    log.info(f'keep_awake_status= {res.status_code}')

def scheduled_job():
    log.info(f"Running schedular {datetime.datetime.now()}")

    keep_awake()

    asd = AmazonScraped()
    deals = asd.get_lightning_deals(MAX_ITEMS)

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
    dbhelper.create_search_history_table()
    main()