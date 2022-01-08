import logging
logging.basicConfig(
    # filename='out.txt',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

import sys
logging.info("syspath= {}", sys.path)

import os
from telegram import Update, ParseMode
from telegram.ext import Updater, CallbackContext, CommandHandler

from amazon_scraped import AmazonScraped

TOKEN = os.environ.get("TOKEN",'')
RESULT_COUNT = int(os.environ.get("RESULT_COUNT", "3"))

def bold(msg):
    return '<b>' + msg + '</b>'

def add_associate_id(url):
    associate_tag = 'onlinesho0a17-21'
    
    breaks = url.split('?',1)
    result_url = breaks[0] + '?tag=' + associate_tag
    if breaks[1] is not None:
        result_url += '&' + breaks[1]
    return result_url

def start(update: Update, context: CallbackContext):
    # context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

    # context.bot.send_message(chat_id, text)

    asd = AmazonScraped()
    deals = asd.get_lightning_deals(RESULT_COUNT)

    for deal in deals:
        offer_title = bold('GET ' + deal['off_percent'] + ' OFF')
        title = bold(deal['title'])
        deal_price = 'Deal Price= ' + deal['deal_price']
        mrp = 'MRP= ' + deal['mrp']
        off_percent = bold('Off Percent= ' + deal['off_percent'])
        rating = deal['rating']
        claim_percent = deal['claim_percent'] + '% claimed'
        time_end = bold(deal['time_end']) + ' after message is posted'
        
        url = add_associate_id(deal['url'])
        
        msg = offer_title + "\n\n" + title + "\n" + deal_price + "\n" + mrp + "\n" + off_percent + "\n" + rating + "\n" + claim_percent + "\n" + time_end + "\n\nBUY NOW:\n" + url
        # logging.info(msg)
        context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode = ParseMode.HTML)



def main():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    # updater.start_polling()

    updater.start_webhook(listen="0.0.0.0",
                          port=5000,
                          url_path=TOKEN)
    updater.bot.setWebhook('https://amazing-deals-app.herokuapp.com/' + TOKEN)

    updater.idle()

if __name__ == '__main__':
    main()