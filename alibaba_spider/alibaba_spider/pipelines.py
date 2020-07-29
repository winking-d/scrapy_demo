# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymysql
from pymysql import cursors
from twisted.enterprise import adbapi


def handle_error(error, item, spider):
    print("=" * 10 + "error" + "=" * 10)
    print(error)
    print("=" * 10 + "error" + "=" * 10)


class AlibabaSpiderPipeline(object):
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
            insert into product_1688(title,buyers,company_name,product_id,product_url) Values(%s,%s,%s,%s,%s)
            """
        return self._sql

    def process_item(self, item, spider):
        defer = self.dbpool.runInteraction(self.insert_item, item)
        defer.addErrback(handle_error, item, spider)

    def insert_item(self, cursor, item):
        print("-" * 50+"写入数据库\n")
        item_info = (
            item["title"], item["buyers"], item["company_name"], item["product_id"], item["product_url"])
        cursor.execute(self.sql, item_info)
