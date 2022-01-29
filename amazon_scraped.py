import re
from amazon_lightning_deals import AmazonLightningDeals

class AmazonScraped:
    def __init__(self):
        pass

    def get_lightning_deals(self, max_deals_count = 10):
        ald = AmazonLightningDeals()
        ald.set_max_deals_count(max_deals_count)

        results = ald.get_lightning_deals_data()

        parsed_results = []

        for deal in results:
            parsed_deal = self.parse_deal(deal)
            parsed_results.append(parsed_deal)


        return parsed_results[:max_deals_count]
    
    def parse_deal(self, deal_info):
        parsed_deal = {}
        
        parsed_deal['title'] = deal_info['title']
        parsed_deal['deal_price'] = deal_info['deal_price']
        parsed_deal['mrp'] = deal_info['mrp']
        parsed_deal['off_percent'] = deal_info['off_percent']
        parsed_deal['rating'] = deal_info['rating']
        parsed_deal['claim_percent'] = deal_info['claim_percent']
        parsed_deal['time_end'] = deal_info['time_end']
        parsed_deal['url'] = deal_info['url']

        parsed_deal['review_count'] = self._get_review_count(deal_info['rating'])
        parsed_deal['off_percent_int'] = self._get_percent_int(deal_info['off_percent'])

        return parsed_deal
    
    def _get_review_count(self, rating):
        res = re.search('\((\d+)[ ]*reviews\)', rating)
        review_cnt = 0
        if res is not None:
            review_cnt = int(res.group(1))
        return review_cnt
    
    def _get_percent_int(self, percent):
        result = 0
        try:
            percent = percent.replace('%', '')
            result = int(percent)
        except Exception as e:
            print(f'percent= {percent}, e= {e}')
        return result

# asd = AmazonScraped()

# print(asd.get_lightning_deals(3))