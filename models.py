class Deal:
    def __init__(self):
        self.offer_title = ''
        self.title = ''
        self.deal_price = ''
        self.mrp = ''
        self.off_percent = ''
        self.rating = ''
        self.claim_percent = ''
        self.time_end = ''
        self.url = ''
        self.updated=''
    def set_deal_data(self, deal):
        self.offer_title = 'GET ' + deal['off_percent'] + ' OFF'
        self.title = deal['title']
        self.deal_price = deal['deal_price']
        self.mrp = deal['mrp']
        self.off_percent = deal['off_percent']
        self.rating = deal['rating']
        self.claim_percent = deal['claim_percent']
        self.time_end = deal['time_end']
        self.url = deal['url']

        # parsed_deal['review_count'] = self._get_review_count(deal_info['rating'])
        # parsed_deal['claim_percent_int'] = self._get_off_percent(deal_info['claim_percent'])
        self.review_count = deal['review_count']
        self.off_percent_int = deal['off_percent_int']

    def __repr__(self):
        return (f'{self.__class__.__name__}('
        f'offer_title= {self.offer_title!r}, title= {self.title!r}, price= {self.deal_price!r}, '
        f'mrp= {self.mrp!r}, off_percent= {self.off_percent!r}, rating= {self.rating!r}, '
        f'review_count= {self.review_count!r}, off_percent_int= {self.off_percent_int!r}, '
        f'claim_percent= {self.claim_percent!r}, time_end= {self.time_end!r}, url= {self.url!r}, updated= {self.updated!r})')

class Item:
    def __init__(self):
        self.id = -""
        self.message = ""
    def __init__(self, id, message):
        self.id = id
        self.message = message

class MultiItems:
    def __init__(self):
        self.message = ""
        self.items = []

    def __init__(self, message, items):
        self.message = message
        self.items = items

    def __str__(self):
        return f"message:{self.message} items:{self.items}"