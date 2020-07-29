import re

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from ..items import ArticleItem


class JsSpider(CrawlSpider):
    name = 'js'
    allowed_domains = ['jianshu.com']
    start_urls = ['https://www.jianshu.com/']

    rules = (
        Rule(LinkExtractor(allow=r'.*/p/[0-9a-z]{12}.*'), callback='parse_detail', follow=True),
    )

    def parse_detail(self, response):
        title = response.xpath("//h1/text()").get()
        avatar = response.xpath("//a[@class='_1OhGeD']/img/@src").get()
        author = response.xpath("//span[@class='FxYr8x']/a/text()").get()
        pup_time = response.xpath("//time/text()").get()
        # mystr = 'adfa\n\n\ndsfsf'8
        # print("".join([s for s in mystr.splitlines(True) if s.strip()]))
        content = "".join(response.xpath("//article//text()").getall())
        content = "".join([s for s in content.splitlines(True) if s.strip()])
        # article_id = re.search(r'/p/([0-9a-z]{12})',response.url).group(1)
        article_id = response.url.split("?")[0].split("/")[-1]
        item = ArticleItem(
            title=title,
            content=content,
            avatar=avatar,
            author=author,
            pup_time=pup_time,
            origin_url=response.url,
            article_id=article_id
        )
        yield item
