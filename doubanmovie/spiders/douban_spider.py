#coding=utf-8
#python默认环境编码为ascii



import sys                          #  为了将爬虫获取到的内容编码为utf-8
reload(sys)                         #
#python默认环境编码时ascii          #
sys.setdefaultencoding("utf-8")     #

from scrapy.spiders import Spider
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from doubanmovie.items import DoubanmovieItem
from doubanmovie.settings import *
import re

class DoubanSpider(Spider):
    name = "douban"
    allowed_domains = ["movie.douban.com"]
    start_urls = []
    headers = HEADERS

    def start_requests(self):
        file_object = open('movie_lists.txt','r')
        url_head = "https://movie.douban.com/subject_search?search_text="
        with open('movie_lists.txt','r') as file_object:
            for line in file_object:
                self.start_urls.append(url_head + line)
            for url in self.start_urls:
                print "+++++++"
                yield Request(url, headers=self.headers, dont_filter=True)


    def parse(self, response):


        hxs = HtmlXPathSelector(response)
        movie_link = hxs.select('//*[@id="content"]/div/div[1]/div[2]/table[1]/tr/td[1]/a/@href').extract()
        if movie_link:
            yield Request(movie_link[0], headers=self.headers, callback=self.parse_item)
        
        
    def parse_item(self,response):
        print "=============START"
        print response.body
        print "=============END"
        hxs = HtmlXPathSelector(response)
        movie_name = hxs.select('//*[@id="content"]/h1/span[1]/text()').extract()
        movie_director = hxs.select('//*[@id="info"]/span[1]/span[2]/a/text()').extract()
        movie_writer = hxs.select('//*[@id="info"]/span[2]/span[2]/a/text()').extract()
        movie_description = hxs.select('//*[@id="link-report"]//*[@property="v:summary"]/text()').extract()
        movie_roles = hxs.select('//*[@id="info"]/span[3]/span[2]//*[@rel="v:starring"]/text()').extract()
        movie_type = hxs.select('//*[@id="info"]//*[@property="v:genre"]/text()').extract()

        #获取电影详细信息序列及字符串
        movie_detail = hxs.select('//*[@id="info"]').extract()
        movie_detail_str = ''.join(movie_detail).strip()

        # 正则匹配关键词
        movie_language_str = '.*语言:</span> (.+?)<br>'.decode("utf8")
        movie_date_str = '.*上映日期:</span> <span property="v:initialReleaseDate" content="(\S+?)">(\S+?)</span>.*'.decode("utf8")
        movie_long_str = '.*片长:</span> <span property="v:runtime" content="(\d+).*'.decode("utf8")
        movie_country_str = '.*制片国家/地区:</span> (.+?)<br>'.decode("utf8")
        
        pattern_language =re.compile(movie_language_str,re.S)
        pattern_date = re.compile(movie_date_str,re.S)
        pattern_long = re.compile(movie_long_str,re.S)
        pattern_country = re.compile(movie_country_str,re.S)
        
        movie_language = re.search(pattern_language,movie_detail_str)
        movie_date = re.search(pattern_date,movie_detail_str)
        movie_long = re.search(pattern_long,movie_detail_str)
        movie_country = re.search(pattern_country,movie_detail_str)


        # 保存数据到item里
        item = DoubanmovieItem()
        item['movie_name'] = self._string_deal(''.join(movie_name))
        item['movie_director'] = self._string_deal(' '.join(movie_director))
        item['movie_description'] = self._string_deal(''.join(movie_description[0])) if len(movie_description) else ''
        item['movie_writer'] = self._string_deal(' '.join(movie_writer))
        item['movie_roles'] = self._string_deal(' '.join(movie_roles))
        item['movie_type'] = self._string_deal(' '.join(movie_type))

        item['movie_language'] = ""
        if movie_language:
            item['movie_language'] = self._string_deal(movie_language.group(1))

        item['movie_date'] = ""
        if movie_date:
            item['movie_date'] = self._string_deal(movie_date.group(1))

        item['movie_long'] = ""
        if movie_long:
            item['movie_long'] = self._string_deal(movie_long.group(1))

        item['movie_country'] = ""
        if movie_country:
            item['movie_country'] = self._string_deal(movie_country.group(1))
        yield item

    def _string_deal(self,data):
        # 由于逗号是拿来分割电影所有信息的，所以需要处理逗号;引号也要处理，否则插入数据库会有问题
        return data.strip().replace(',',';').replace('\'','\\\'').replace('\"','\\\"').replace(':',';')
