import re

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from ..items import AlibabaSpiderItem


class A1688SpiderSpider(CrawlSpider):
    keyword = "paper"
    name = '1688_spider'
    allowed_domains = ['www.alibaba.com']
    start_urls = ['https://www.alibaba.com/products/'+keyword+'.html?IndexArea=product_en&page=1']

    rules = (
        Rule(LinkExtractor(allow=r'.+/products/'+keyword+'.html?.*IndexArea=product_en&page=\d+.*'), follow=True),
        Rule(LinkExtractor(allow=r'.*product-detail/.*'), callback='parse_product', follow=False),
    )

    def parse_product(self, response):
        print("-" * 40+"获取信息\n")
        title = response.xpath("//h1/text()").get()
        try:
            buyers = re.search(r'\d+', response.xpath("//div[@class='sold-quantity']/span/text()").get()).group()
        except:
            buyers = 0
        company_name = response.xpath("//div[@class='company-name-container']/a/@title").get()
        product_id = re.search(r'(\d+).html', response.url).group(1)
        product_url = response.url
        item = AlibabaSpiderItem(
            title=title,
            buyers=buyers,
            company_name=company_name,
            product_id=product_id,
            product_url=product_url
        )
        yield item
