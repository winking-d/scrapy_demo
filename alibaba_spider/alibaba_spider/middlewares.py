# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import json
import random
import re
import time
# import logging

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy.http.response.html import HtmlResponse

# log = logging.getLogger('scrapy.proxies')


class AlibabaSpiderDownloaderMiddleware(object):
    def __init__(self):
        chrome_options = Options()
        prefs = {
            'profile.default_content_setting_values': {
                'images': 2,  # 不加载图片
                'stylesheet': 2,  # 不加载css
            }
        }
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument('--disable-gpu')
        # chrome_options.add_argument('--headless')  # 无浏览器模式
        self.driver = webdriver.Chrome(options=chrome_options)

    def process_request(self, request, spider):
        self.driver.get(request.url)
        list_page = re.search(r'.+/products/[a-zA-Z]*.html.+', request.url)
        if list_page:
            print("-" * 100 + "列表页面\n")
            self.driver.execute_script("window.scrollTo(100, document.body.scrollHeight);")  # 滑倒页面底部
            time.sleep(0.2)
        else:
            print("-" * 30 + "详情页面\n")
            time.sleep(2.5)
        source = self.driver.page_source
        response = HtmlResponse(url=self.driver.current_url, body=source, request=request, encoding='utf-8')
        return response


class UserAgentDownloaderMiddleware(object):
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/44.0.2403.155 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2226.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.4; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36'
    ]

    def process_request(self, request, spider):
        user_agent = random.choice(self.USER_AGENTS)
        request.headers['User_Agent'] = user_agent


class RandomProxy(object):
    def __init__(self, settings):
        self.PROXY_URL = settings.get('PROXY_URL')
        self.chosen_proxy = ''

        if self.PROXY_URL is None:
            raise KeyError('需要先设置获取代理ip接口的地址')
        # 从地址获取一个ip
        self.chosen_proxy = self.getProxy()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def getProxy(self):
        print('get proxy')
        proxy_addr = json.loads(requests.get(self.PROXY_URL).text)['ip']
        print("[+]---get proxy ip is:" + proxy_addr)
        return proxy_addr

    def delip(self, proxy):
        print("要删除的ip:" + proxy)
        sql = 'delete from ip where data =%s' % '\'' + proxy + '\''
        sta = cursor.execute(sql)
        print(sql)
        print(sta)
        if sta > 0:
            print("del band ip from databases")
            db.connection.commit()
        else:
            print('del ip faile')

    def process_request(self, request, spider):
        if 'proxy' in request.meta:
            if request.meta["exception"] is False:
                return
        request.meta["exception"] = False
        request.meta['proxy'] = "http://" + self.chosen_proxy

    def process_response(self, request, response, spider):

        if response.status in [403, 400, 302] and 'proxy' in request.meta:
            print('Response status: {0} using proxy {1} retrying request to {2}'.format(response.status, \
                                                                                          request.meta['proxy'],
                                                                                          request.url))
            proxy = request.meta['proxy']
            del request.meta['proxy']
            proxyip = proxy.split("//")[1]
            try:
                # 删除数据库里的ip
                self.delip(proxyip)
                print('deleted banned proxy , proxy %s' % proxyip)
            except KeyError:
                pass
            self.chosen_proxy = self.getProxy()  # 这个代理被403,302了 重新获取
            return request
        return response

    def process_exception(self, request, exception, spider):
        if 'proxy' not in request.meta:
            print("没代理错了,需要检查")
            return
        else:
            print("有代理也错了，把数据库的ip删掉")
            proxy = request.meta['proxy']
            proxyip = proxy.split("//")[1]
            try:
                # 删除数据库里的ip
                self.delip(proxyip)
            except KeyError:
                pass
            request.meta["exception"] = True
            print("重新获取ip")
            self.chosen_proxy = self.getProxy()
            return request
