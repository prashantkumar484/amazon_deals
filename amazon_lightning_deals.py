### SELENIUM IMPORTS START ###
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import visibility_of_element_located, visibility_of_all_elements_located, presence_of_all_elements_located
from selenium.webdriver.support.wait import WebDriverWait
### SELENIUM IMPORTS END ###

from urllib.parse import urlencode
from bs4 import BeautifulSoup
import json
import time
import gc
import logging as logger

logger.basicConfig(
    # filename='out.txt',
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logger.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

from selenium_util import SeleniumUtil


class AmazonLightningDeals:
    def __init__(self):
        self.base_url = 'https://www.amazon.in'
        self.url_endpoint = '/gp/goldbox/'
        self.curr_view_index = 0

        self.max_deals_count = 50

        self.set_selector()
        self.set_parent_selector()
        self.create_complete_url()
    
    def set_max_deals_count(self, cnt):
        self.max_deals_count = cnt

    def get_lightning_deals_data(self):

        selenium_util = SeleniumUtil()
        driver = selenium_util.get_new_driver_obj()

        deals = []
        count = 1
        while count > 0:
            print(f'gc_count_before= {gc.get_count()}')
            print(f'gc_collected= {gc.collect()}')
            print(f'gc_count_after= {gc.get_count()}')
            logger.info(f'Trying for index= {self.curr_view_index}')
            if self.curr_view_index%100 ==0:
                driver.close()
                time.sleep(5)
                logger.info(f'Creating new driver.. index= {self.curr_view_index}')
                del driver
                driver = selenium_util.get_new_driver_obj()
            else:
                time.sleep(2)

            self.create_complete_url()

            # page_data = self.get_page_data(driver)
            # # logger.info(f'pageData= {page_data}')
            # deals_list = self.get_deals_list(page_data)
            deals_list = self.get_page_data(driver)
            # logger.info(f'deals_list count= {len(deals_list)}')
            deals = deals + deals_list
            count = len(deals_list)
            # if(count>0):
            #     break
            # logger.info(count)
            print(f'gc_count_before= {gc.get_count()}')
            print(f'gc_collected= {gc.collect()}')
            print(f'gc_count_after= {gc.get_count()}')
            if len(deals) > self.max_deals_count:
                break
        # logger.info(deals[-3:-1])
        logger.info(f'Total deals count= {len(deals)}')

        # logger.debug(f'Deals:\n {deals}')

        driver.close()
        del driver
        print(f'gc_count_before= {gc.get_count()}')
        print(f'gc_collected= {gc.collect()}')
        print(f'gc_count_after= {gc.get_count()}')

        return deals


    
    def get_deals_list(self, page_data):
        soup = BeautifulSoup(page_data, 'html.parser')
        results = soup.findAll('div', {
            'data-testid': "deal-card"
        })

        return results
    
    def get_deal_info(self, elements):
        # https://towardsdatascience.com/in-10-minutes-web-scraping-with-beautiful-soup-and-selenium-for-data-professionals-8de169d36319
        result = []

        for el in elements:
            # print(f'gc_count_before= {gc.get_count()}')
            # print(f'gc_collected= {gc.collect()}')
            # print(f'gc_count_after= {gc.get_count()}')
            try:
                deal_info = {}

                # anchors = el.find_elements_by_tag_name('a')
                # divs = el.find_elements_by_tag_name('div')

                anchors = el.find_elements(By.TAG_NAME, 'a')
                divs = el.find_elements(By.TAG_NAME, 'div')

                title = anchors[2].find_element(By.TAG_NAME, 'div').text

                # logger.info(f'a= {anchors[1].get_attribute("outerHTML")}')
                price_amount = anchors[1].find_element(By.CSS_SELECTOR, "span > span.a-price > span > span.a-price-whole").text
                price_symbol = anchors[1].find_element(By.CSS_SELECTOR, "span > span.a-price > span > span.a-price-symbol").text
                deal_price = price_symbol + ' ' + price_amount

                mrp_amount = anchors[1].find_element(By.CSS_SELECTOR, "div > span > span.a-price > span > span.a-price-whole").text
                mrp_symbol = anchors[1].find_element(By.CSS_SELECTOR, "div > span > span.a-price > span > span.a-price-symbol").text
                mrp = mrp_symbol + ' ' + mrp_amount
                
                off_percent = anchors[1].find_element(By.CSS_SELECTOR, 'div.a-row > span.a-color-secondary').text
                off_percent = off_percent.split()[-2]
                
                rating = el.find_element(By.CSS_SELECTOR, "div > a[data-testid='link-review-component']").get_attribute("aria-label")

                claim_percent_text = el.find_element(By.XPATH, ".//div[@class[contains(.,'claimedPercentage')]]").text
                claim_percent = claim_percent_text.split()[0][:-1]

                time_end = el.find_element(By.XPATH, ".//div[@class[contains(.,'claimBarEndTimer')]]/span").text

                url = el.find_element(By.XPATH, ".//a/div[@class[contains(.,'DealContent')]]/parent::a").get_attribute('href')

                # deal_price, mrp, off_percent, claim_percent, time_end
                deal_info['title'] = str(title)
                deal_info['deal_price'] = str(deal_price)
                deal_info['mrp'] = str(mrp)
                deal_info['off_percent'] = str(off_percent)
                deal_info['rating'] = str(rating)
                deal_info['claim_percent'] = str(claim_percent)
                deal_info['time_end'] = str(time_end)
                deal_info['url'] = str(url)
                result.append(deal_info)
            except:
                pass
        return result
    
    def get_page_data(self, driver, timeout=10, poll_frequency=1):
        driver.get(self.url)
    
        wait = WebDriverWait(driver, timeout, poll_frequency)

        data_container = visibility_of_element_located(
            (self.parent_selector_type, self.parent_selector_field))

        dd = wait.until(data_container)

        total_child_elements = int(dd.get_property('childElementCount'))

        logger.info(f'Total= {total_child_elements}')

        count = 0
        no_deals = False
        elements = []

        while count < total_child_elements:
            time.sleep(3)
            # Checking if last page reached.. i.e. no-deals-message div is present
            el = driver.find_elements(self.selector_type ,"[data-testid='no-deals-message']")
            if len(el)>0:
                no_deals = True
                del el
                return []
            
            del el

            logger.info("count < total_child_elements .... Trying.....")
            time.sleep(3)
            elements = driver.find_elements(self.selector_type ,self.selector_field)
            count = len(elements)
            logger.info(f'found count= {count}')

            if count < total_child_elements:
                del elements

            print(f'gc_count_before= {gc.get_count()}')
            print(f'gc_collected= {gc.collect()}')
            print(f'gc_count_after= {gc.get_count()}')
        
        logger.info(f'Total Elements found = {count}')

        # data = driver.page_source

        ### Getting deal data
        data = self.get_deal_info(elements)
        del elements

        # update index for next page
        self.curr_view_index += count

        # return data
        return data

    def get_params(self, view_index=0):
        params = {
            'ie': 'UTF8',
            'ref_': 'topnav_storetab_gb',
            'deals-widget': {
                "version":1,
                "viewIndex":view_index,
                "presetId":"deals-collection-lightning-deals",
                "dealType":"LIGHTNING_DEAL",
                "sorting":"BY_DISCOUNT_DESCENDING",
                "starRating":3
            }
        }

        return params

    def create_complete_url(self):

        result_url = self.base_url + self.url_endpoint + '?'

        params = self.get_params(self.curr_view_index)
        
        result_url += urlencode({k: json.dumps(v) for k, v in params.items()})

        self.url = result_url
        logger.info(f'result_url= {result_url}')
        return result_url
    
    def set_parent_selector(self, parent="[data-testid='grid-deals-container']", selector_type='css_selector',):
        if selector_type== 'css_selector':
            self.parent_selector_type = By.CSS_SELECTOR
            self.parent_selector_field = parent
    
    def set_selector(self, element="[data-testid='deal-card']", selector_type='css_selector',):
        if selector_type== 'css_selector':
            self.selector_type = By.CSS_SELECTOR
            self.selector_field = element
