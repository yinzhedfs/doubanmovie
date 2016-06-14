#coding=utf-8
import sys
reload(sys)
#python默认环境编码时ascii
#coding=utf-8


import sys                          #  为了将爬虫获取到的内容编码为utf-8
reload(sys)                         #
#python默认环境编码时ascii          #
sys.setdefaultencoding("utf-8")     #

from scrapy.spiders import Spider
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from doubanmovie.items import DoubanmovieItem
import re

class DoubanSpider(Spider):
    name = "douban"
    allowed_domains = ["movie.douban.com"]
    start_urls = []
    headers = {
        'Host':'movie.douban.com',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate, br',
        'Accept-Language':'zh,zh-HK;q=0.8,zh-CN;q=0.7,en-US;q=0.5,en;q=0.3,el;q=0.2',
        'Connection':'keep-alive',
        'Cache-Control':'max-age=0',
        'DNT':'1',
        'Referer':None #注意如果依然不能抓取的话，这里可以设置抓取网站的host
    }

    def start_requests(self):
        file_object = open('movie_lists.txt','r')

        try:
            url_head = "https://movie.douban.com/subject_search?search_text="
            for line in file_object:
                self.start_urls.append(url_head + line)
            for url in self.start_urls:
                # requests = self.make_requests_from_url(url)
                # yield requests
                # print requests
                print "+++++++"
                yield Request(url, headers=self.headers, dont_filter=True)
                # if type(requests) is list:
                #     for request in requests:
                #         yield request
                # else:
                #     yield requests
        finally:
            file_object.close()
            #years_object.close()

    def parse(self, response):
        print "=============START"
        print response.body
        print "=============END"
        #open("test.html",'wb').write(response.body)
        hxs = HtmlXPathSelector(response)
        #movie_name = hxs.select('//*[@id="content"]/div/div[1]/div[2]/table[1]/tr/td[1]/a/@title').extract()
        movie_link = hxs.select('//*[@id="content"]/div/div[1]/div[2]/table[1]/tr/td[1]/a/@href').extract()
        #movie_desc = hxs.select('//*[@id="content"]/div/div[1]/div[2]/table[1]/tr/td[2]/div/p/text()').extract()

        if movie_link:
            yield Request(movie_link[0], headers=self.headers, callback=self.parse_item)
        
        
    def parse_item(self,response):
        hxs = HtmlXPathSelector(response)
        movie_name = hxs.select('//*[@id="content"]/h1/span[1]/text()').extract()
        movie_director = hxs.select('//*[@id="info"]/span[1]/span[2]/a/text()').extract()
        movie_writer = hxs.select('//*[@id="info"]/span[2]/span[2]/a/text()').extract()
        #爬取电影详情需要在已有对象中继续爬取
        movie_description_paths = hxs.select('//*[@id="link-report"]')
        movie_description = []
        for movie_description_path in movie_description_paths:
            movie_description = movie_description_path.select('.//*[@property="v:summary"]/text()').extract()

        #提取演员需要从已有的xPath对象中继续爬我要的内容
        movie_roles_paths = hxs.select('//*[@id="info"]/span[3]/span[2]')
        movie_roles = []
        for movie_roles_path in movie_roles_paths:
            movie_roles = movie_roles_path.select('.//*[@rel="v:starring"]/text()').extract()

        #获取电影详细信息序列
        movie_detail = hxs.select('//*[@id="info"]').extract()

        item = DoubanmovieItem()
        item['movie_name'] = ''.join(movie_name).strip().replace(',',';').replace('\'','\\\'').replace('\"','\\\"').replace(':',';')
        #item['movie_link'] = movie_link[0]
        item['movie_director'] = movie_director[0].strip().replace(',',';').replace('\'','\\\'').replace('\"','\\\"').replace(':',';') if len(movie_director) > 0 else ''
        #由于逗号是拿来分割电影所有信息的，所以需要处理逗号;引号也要处理，否则插入数据库会有问题
        item['movie_description'] = movie_description[0].strip().replace(',',';').replace('\'','\\\'').replace('\"','\\\"').replace(':',';') if len(movie_description) > 0 else ''
        item['movie_writer'] = ';'.join(movie_writer).strip().replace(',',';').replace('\'','\\\'').replace('\"','\\\"').replace(':',';')
        item['movie_roles'] = ';'.join(movie_roles).strip().replace(',',';').replace('\'','\\\'').replace('\"','\\\"').replace(':',';')
        #item['movie_language'] = movie_language[0].strip() if len(movie_language) > 0 else ''
        #item['movie_date'] = ''.join(movie_date).strip()
        #item['movie_long'] = ''.join(movie_long).strip()
        
        #电影详情信息字符串
        movie_detail_str = ''.join(movie_detail).strip()
        #print movie_detail_str

        movie_language_str = ".*语言:</span> (.+?)<br>".decode("utf8")
        movie_date_str = ".*上映日期:</span> <span property=\"v:initialReleaseDate\" content=\"(\S+?)\">(\S+?)</span>.*".decode("utf8")
        movie_long_str = ".*片长:</span> <span property=\"v:runtime\" content=\"(\d+).*".decode("utf8")
        
        pattern_language =re.compile(movie_language_str,re.S)
        pattern_date = re.compile(movie_date_str,re.S)
        pattern_long = re.compile(movie_long_str,re.S)
        
        
        movie_language = re.search(pattern_language,movie_detail_str)
        movie_date = re.search(pattern_date,movie_detail_str)
        movie_long = re.search(pattern_long,movie_detail_str)
        print "电影语言==========" + str(movie_language)
        print "电影日期==========" + str(movie_date)
        print "电影时长==========" + str(movie_long)

        item['movie_language'] = ""
        if movie_language:
            item['movie_language'] = movie_language.group(1).strip().replace(',',';').replace('\'','\\\'').replace('\"','\\\"').replace(':',';')
        #item['movie_detail'] = ''.join(movie_detail).strip()

        item['movie_date'] = ""
        if movie_date:
            item['movie_date'] = movie_date.group(1).strip().replace(',',';').replace('\'','\\\'').replace('\"','\\\"').replace(':',';')

        item['movie_long'] = ""
        if movie_long:
            item['movie_long'] = movie_long.group(1)

        yield item
