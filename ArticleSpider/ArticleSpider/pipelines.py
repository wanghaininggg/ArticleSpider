# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
import MySQLdb
import MySQLdb.cursors
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonWithEncodingPipeline(object):
    # 自定义json文件的导出
    def __init__(self):
        self.file = codecs.open('article.json', 'w', encoding="utf-8")  # 初始化打开文件

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n" # ensure-ascii中文显示
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.close()


class JsonExporterPipleline(object):
    """
    调用scrapy提供的json export导出json文件
    """
    def __init__(self):

        self.file = open('articleexport.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii = False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()    # 调用 export的方法
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class MysqlPipeline(object):
    """
    自定义数据保存到Mysql
    """
    def __init__(self):
        # 连接数据库
        self.conn = MySQLdb.connect(host='localhost', user='root', passwd='2536340900', db='article_spider', charset='utf8', use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
        insert into article values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.cursor.execute(insert_sql, (item['title'], item['create_date'], item['url'], item['url_object_id'], item['front_image_url'], item['front_image_path'], item['comment_nums'], item['fav_nums'], item['praise_nums'], item['tags'], item['content']))
        self.conn.commit()


class MysqlTwistedPipLine(object):
    # 异步保存到Mysql数据库
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
        host=settings["MYSQL_HOST"], # 获取setting中定义的值
        db = settings["MYSQL_DBNAME"],
        user = settings["MYSQL_USER"],
        passwd = settings["MYSQL_PASSWORD"],
        charset = 'utf8',
        cursorclass = MySQLdb.cursors.DictCursor,
        use_unicode=True
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)
        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error()) # 处理异常

    def handle_error(self, failure, item, spider):
        print(failure)  # 处理异步插入的异常

    def do_insert(self, cursor, item):
        insert_sql = """
          insert into article values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
          """
        cursor.execute(insert_sql, (
        item['title'], item['create_date'], item['url'], item['url_object_id'], item['front_image_url'],
        item['front_image_path'], item['comment_nums'], item['fav_nums'], item['praise_nums'], item['tags'],
        item['content']))


class ArticleImagePipeLine(ImagesPipeline):
    """
    获取图片保存路径
    """
    def item_completed(self, results, item, info):
        for ok, value in results:
            if "front_image_url" in item:
                image_file_path = value["path"]
                item["front_image_path"] = image_file_path
            return item


