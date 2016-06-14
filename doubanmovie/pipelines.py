# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import codecs

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

