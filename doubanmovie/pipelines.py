# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import codecs
import pymongo
from doubanmovie.items import DoubanmovieItem

class DoubanmoviePipeline(object):
    def __init__(self):
        # 保存数据到该文件
        self.file = codecs.open('result.txt',mode='wb',encoding='utf-8')

    def process_item(self, item, spider):
        # 将item里的数据转为json后写入文件
        # lines = json.dumps(dict(item),ensure_ascii=False) + '\n'
        # self.file.write(lines)
        # 将每个item转为字典，将字典每个键值分行写入文件
        item_dict = dict(item)
        for line in item_dict:
            attr = str(line) + ': ' + item_dict[line] + '\n'
            self.file.write(attr)

        self.file.write('\n\n\n')
        return item

class MongoDBPipeline(object):
    def __init__(self):
        # 保存数据到mongodb的douban.db_movies里
        connection = pymongo.MongoClient("localhost", 27017)
        self.db = connection["douban"]
        self.db_movies = self.db["db_movies"]


    def process_item(self, item, spider):
        if isinstance(item, DoubanmovieItem):
            self.saveOrUpdate(self.db_movies,item)
        return item

    def saveOrUpdate(self,collection,item):
        movie_name = dict(item).get("movie_name")
        movie_date = dict(item).get("movie_date")

        if movie_name is not None:
            tmp = collection.find_one({"movie_name":movie_name,"movie_date":movie_date})
            #数据库不存在
            if tmp is None:
                print movie_name
                collection.insert(dict(item))
                #TODO 暂时只插入不更新
            # else:
            #     collection.update({"movie_name":movie_name},dict(item))
        else:
            collection.insert(dict(item))