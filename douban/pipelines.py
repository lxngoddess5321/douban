# -*- coding: utf-8 -*-
import redis
import json
import pymysql
import os
import urllib.request as ur

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class DoubanPipeline(object):
    def __init__(self):
        # redis连接
        self.pool = redis.ConnectionPool(host="localhost", port=6379, decode_responses=True)
        self.rdb = redis.Redis(connection_pool=self.pool)
        # 计数值
        self.num = 1
        # 本地文本记录
        self.f = open("movies.json", "w")
        # 本地图片存放路径
        self.dirpath = "/home/sedlice/PycharmProjects/douban/cover/"
        if not os.path.exists(self.dirpath):
            os.mkdir(self.dirpath)

    def process_item(self, item, spider):
        # 返回的item写入本地文本文件
        self.f.write(json.dumps(dict(item), ensure_ascii=False) + "\n")
        # 返回的item写入redis
        self.rdb.lpush(str(self.num), item["name"])
        self.rdb.lpush(str(self.num), item["actor"])
        self.rdb.lpush(str(self.num), item["m_type"])
        self.rdb.lpush(str(self.num), item["score"])
        self.rdb.lpush(str(self.num), item["summary"])
        self.rdb.lpush(str(self.num), item["imgurl"])
        self.rdb.lpush(str(self.num), item["detail"])
        self.rdb.lpush(str(self.num), item["watchplace"])
        self.rdb.lpush(str(self.num), item["rankno"])
        # 设置文件名和路径名
        imgname = item["rankno"] + ".jpg"
        pathimgname = os.path.join(self.dirpath, imgname)
        # 调用requests模块的方法下载图片并写入到本地
        ur.urlretrieve(item["imgurl"], pathimgname)
        # 计数值自增
        self.num += 1
        return item

    def close_spider(self, spider):
        # MySQL连接
        conn = pymysql.connect(user="root", password="root", host="localhost", charset="utf8")
        conn.select_db("spider")
        curr = conn.cursor()
        # 计数值
        fnum = 1
        # 循环读取redis数据并存入MySQL数据库
        while fnum <= self.rdb.dbsize():
            curr.execute("insert into spider.doubanmovies(name,actor,mtype,score,summary,imgurl,detail,watchplace,rankno) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)", (
                self.rdb.lindex(str(fnum), 8),
                self.rdb.lindex(str(fnum), 7),
                self.rdb.lindex(str(fnum), 6),
                self.rdb.lindex(str(fnum), 5),
                self.rdb.lindex(str(fnum), 4),
                self.rdb.lindex(str(fnum), 3),
                self.rdb.lindex(str(fnum), 2),
                self.rdb.lindex(str(fnum), 1),
                self.rdb.lindex(str(fnum), 0)
            ))
            conn.commit()
            fnum += 1
        # 关闭文本记录文件
        self.f.close()
