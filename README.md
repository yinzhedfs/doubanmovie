## scrapy抓取豆瓣电影详情

#### 配置scrapy运行环境
```
pip install scrapy
```
或
```
pip install -r requirements.txt
```

#### scrapy设置
* items.py 设置所要抓取的信息

```python
class DoubanmovieItem(Item):
    # define the fields for your item here like:
    movie_name = Field()
    movie_director = Field()
    movie_writer = Field()
    movie_roles = Field()
    movie_language = Field()
    movie_date = Field()
    movie_long = Field()
    movie_description = Field()
    movie_type = Field()
    movie_country = Field()

```
* spiders/douban_spider.py 是爬虫的主体，用于抓取数据，返回item
  * 设置爬虫名
```
name = "douban"
```
* pipelines.py 用于处理爬虫返回的item数据
  * 分别存储在文本和数据库里

```python
class DoubanmoviePipeline(object):
    def __init__(self):
        # 保存数据到该文件
        self.file = codecs.open('result.txt',mode='wb',encoding='utf-8')

    def process_item(self, item, spider):
        # 将每个item转为字典，将字典每个键值分行写入文件
        item_dict = dict(item)
        for line in item_dict:
            attr = str(line) + ': ' + item_dict[line] + '\n'
            self.file.write(attr)

        self.file.write('\n\n\n')
        return item

```

```python
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
```
* settings.py 设置scrapy的一些功能
  * 设置pipelines,分别调用pipelines里的类处理数据，后面数字越小，优先级越高
```
ITEM_PIPELINES = {
   'doubanmovie.pipelines.DoubanmoviePipeline': 2,
   'doubanmovie.pipelines.MongoDBPipeline': 1,
}
```
  * 设置USER_AGENT，防止被ban(可在爬虫里手动设置headers,更改Request请求头)
```
USER_AGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0'
```
  * 设置DOWNLOAD_DELAY,减少对服务器的压力，但速度会变慢
```
DOWNLOAD_DELAY = 0.5
```

* 更改movie_lists.txt文件，将所要爬取的电影名添加进去

```
movie_name1
movie_name2
movie_name3
```
#### mongodb设置
```
> use douban                          #新建库
> db.createCollection('db_movies')    #新建存储电影数据的集合
```

#### scrapy进行爬取
```
scrapy crawl douban
```
#### 爬取结果储存在result.txt文件里和mongdb里douban.db_movies
