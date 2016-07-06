# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Item,Field

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
