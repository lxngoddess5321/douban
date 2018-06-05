# -*- coding: utf-8 -*-
import scrapy
from douban.items import DoubanItem


class DoubanspiderSpider(scrapy.Spider):
    name = 'doubanspider'
    allowed_domains = ['douban.com']
    offset = 0
    base_url = "https://movie.douban.com/top250?start="
    # 如果不需要登录时使用下方代码
    start_urls = [base_url + "0"]
    # 需要登录时使用下方代码
    # start_urls = ["https://accounts.douban.com/login"]

    def parse(self, response):
        '''
        爬虫启动时执行的方法
        '''
        # 如果需要登录时使用下方两句
        # form_data = {"form_email": "419345180@qq.com", "form_password": "Peng19921110"}
        # return scrapy.FormRequest.from_response(
        #     response,
        #     formdata=form_data,
        #     callback=self.after_login
        # )
        # 如果不需要登录时使用下方代码
        yield scrapy.Request(self.base_url + str(self.offset), callback=self.after_login)

    def after_login(self, response):
        '''
        登录后执行方法（即爬虫主体方法）
        '''
        # 获取页面所有目标的集合数据
        item_list = response.xpath("//div[@class='item']/div[@class='info']")
        for i in item_list:
            # 声明一个item对象
            item = DoubanItem()
            # 获取电影详细页面的url链接
            detail_url = i.xpath("./div[@class='hd']/a/@href").extract()[0]
            item["name"] = i.xpath("./div[@class='hd']/a/span/text()").extract()[0].replace(" ", "").replace("\xa0", "")
            item["imgurl"] = i.xpath("//div[@class='item']/div[@class='pic']/a/img/@src").extract()[0]
            item["actor"] = i.xpath("./div[@class='bd']/p[1]/text()").extract()[0].replace(" ", "").replace("\xa0", "").replace("\n", "")
            item["m_type"] = i.xpath("./div[@class='bd']/p[1]/text()").extract()[1].replace(" ", "").replace("\xa0", "").replace("\n", "")
            item["score"] = i.xpath("./div[@class='bd']/div[@class='star']/span[@class='rating_num']/text()").extract()[0]
            # 部分列表页上的电影存在无简介情况，所以做判断区别设置
            if len(i.xpath("./div[@class='bd']/p[@class='quote']/span[@class='inq']/text()")) > 0:
                item["summary"] = i.xpath("./div[@class='bd']/p[@class='quote']/span[@class='inq']/text()").extract()[0]
            else:
                item["summary"] = ""
            # 将详细页面的链接交给引擎，调用处理详细信息页面的方法处理页面数据
            yield scrapy.Request(url=detail_url, meta={"item_main": item}, callback=self.detail_page)
        if self.offset < 25:
            self.offset += 25
            next_url = self.base_url + str(self.offset)
            # 递归执行自身，分析获取下一页的数据
            yield scrapy.Request(next_url, callback=self.after_login)

    def detail_page(self, response):
        '''
        电影详细信息页面的分析处理方法
        '''
        # 获取传入的item数据
        item = response.meta["item_main"]
        item["rankno"] = response.xpath("//span[@class='top250-no']/text()").extract()[0]
        # 切片将数据开头的”No.“去除，只留下排名数值
        item["rankno"] = item["rankno"][3:]
        # 简介存在两种情况，if处理的是简介较长时的情况，else处理的是简介较短情况时的情况
        if len(response.xpath("//div[@id='link-report']/span[@class='short']")) > 0:
            item["detail"] = response.xpath("//div[@id='link-report']/span[@class='all hidden']/text()").extract()
            item["detail"] = "".join(item["detail"])
            item["detail"] = item["detail"].replace(" ", "").replace("\n", "")
        else:
            item["detail"] = response.xpath("//div[@id='link-report']/span[1]/text()").extract()
            item["detail"] = "".join(item["detail"])
            item["detail"] = item["detail"].replace(" ", "").replace("\n", "")
        item["watchplace"] = response.xpath("//ul[@class='bs']/li/a/@data-cn").extract()
        # 将获取的列表拼成字符串储存
        item["watchplace"] = ",".join(item["watchplace"])
        yield item
