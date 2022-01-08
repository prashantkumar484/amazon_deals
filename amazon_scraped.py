from amazon_lightning_deals import AmazonLightningDeals

class AmazonScraped:
    def __init__(self):
        pass

    def get_lightning_deals(self, max_deals_count = 10):
        ald = AmazonLightningDeals()
        ald.set_max_deals_count(max_deals_count)

        results = ald.get_lightning_deals_data()

        return results[:max_deals_count]

# asd = AmazonScraped()

# print(asd.get_lightning_deals(3))