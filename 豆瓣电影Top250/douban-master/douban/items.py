# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DoubanItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    #序号
    serial_name = scrapy.Field()
    #电影名
    movie_name = scrapy.Field()
    #电影介绍
    introduce = scrapy.Field()
    #电影星级
    star = scrapy.Field()
    #电影评论数
    evaluate = scrapy.Field()
    #电影的描述
    describe = scrapy.Field()
