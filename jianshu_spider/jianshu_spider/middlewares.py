# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import time

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
from selenium import webdriver
from scrapy.http.response.html import HtmlResponse


class SeleniumDownloadMiddleware(object):
    def __init__(self):
        self.driver = webdriver.Chrome(
            executable_path=r"C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe")

    def process_request(self, request, spider):
        self.driver.get(request.url)
        # time.sleep(0.1)
        try:
            while True:
                showMore = self.driver.find_elements_by_class_name("H7E3vT")
                showMore.click()
                # time.sleep(0.1)
                if not showMore:
                    break
        except:
            pass
        source = self.driver.page_source
        response = HtmlResponse(url=self.driver.current_url, body=source, request=request, encoding='utf-8')
        return response
