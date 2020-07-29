# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymysql
from twisted.enterprise import adbapi
from pymysql import cursors


# class JianshuSpiderPipeline:
#     def __init__(self):
#         dbparams = {
#             'host': '127.0.0.1',
#             'port': 3306,
#             'user': 'root',
#             'password': 'root',
#             'database': 'scrapy_demo',
#             'charset': 'utf8'
#         }
#         # self.conn = pymysql.connect(host:'127.0.0.1',port=''...)
#         self.conn = pymysql.connect(**dbparams)
#         self.cursor = self.conn.cursor()
#         self._sql = None
#
#     @property
#     def sql(self):
#         if not self._sql:
#             self._sql = """
#             insert into article(title,content,article_id,origin_url,author,avatar,pup_time) Values(%s,%s,%s,%s,%s,%s,%s)
#             """
#         return self._sql
#
#     def process_item(self, item, spider):
#         item_info = (
#             item["title"], item["content"], item["article_id"], item["origin_url"], item["author"], item["avatar"],
#             item["pup_time"])
#         self.cursor.execute(self._sql, item_info)
#         return item
#
#
def handle_error(error, item, spider):
    print("=" * 10 + "error" + "=" * 10)
    print(error)
    print("=" * 10 + "error" + "=" * 10)


class JianshuTwistedPipeline(object):
    def __init__(self):
        dbparams = {
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'root',
            'password': 'root',
            'database': 'scrapy_demo',
            'charset': 'utf8',
            'cursorclass': cursors.DictCursor
        }
        self.dbpool = adbapi.ConnectionPool('pymysql', **dbparams)
        self._sql = None

    @property
    def sql(self):
        if not self._sql:
            self._sql = """
            insert into article(title,content,article_id,origin_url,author,avatar,pup_time) Values(%s,%s,%s,%s,%s,%s,%s)
            """
        return self._sql

    def process_item(self, item, spider):
        defer = self.dbpool.runInteraction(self.insert_item, item)
        defer.addErrback(handle_error, item, spider)

    def insert_item(self, cursor, item):
        item_info = (
            item["title"], item["content"], item["article_id"], item["origin_url"], item["author"], item["avatar"],
            item["pup_time"])
        cursor.execute(self.sql, item_info)
