# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DoubanItem(scrapy.Item):
    # define the fields for your item here like:
    # 电影排名编号
    rankno = scrapy.Field()
    # 电影名
    name = scrapy.Field()
    # 电影封面图片url
    imgurl = scrapy.Field()
    # 列表页演职员展示
    actor = scrapy.Field()
    # 列表页电影类型介绍
    m_type = scrapy.Field()
    # 豆瓣评分
    score = scrapy.Field()
    # 列表页电影简述
    summary = scrapy.Field()
    # 电影内容页电影简介
    detail = scrapy.Field()
    # 观看网站名称
    watchplace = scrapy.Field()
