import scrapy
from douban.items import DoubanItem

class DoubanSpiderSpider(scrapy.Spider):
    #爬虫名
    name = 'douban_spider'
    #允许的域名
    allowed_domains = ['movie.douban.com']
    #入口url
    start_urls = ['https://movie.douban.com/top250']

    #默认解析方法
    def parse(self, response):
        movie_list = response.xpath("//div[@class='article']//ol[@class='grid_view']/li");
        for item in movie_list:
            #item文件导入
            douban_item = DoubanItem()
            douban_item['serial_name'] = item.xpath(".//div[@class='item']//div[@class='pic']/em/text()").extract_first()
            douban_item['movie_name'] = item.xpath(".//div[@class='item']//div[@class='info']//div[@class='hd']/a/span[1]/text()").extract_first()

            # indroduce包含多行，空格；需要额外处理。
            content = item.xpath(".//div[@class='item']//div[@class='info']//div[@class='bd']/p[1]/text()").extract()
            for i_content in content:
                content_s = "".join(i_content.split())  #split处理字符串，去除换行与空格
                douban_item['introduce'] = content_s
            douban_item['star'] = item.xpath(".//div[@class='item']//div[@class='info']//div[@class='bd']//div[@class='star']//span[@class='rating_num']/text()").extract_first()
            douban_item['evaluate'] = item.xpath(".//div[@class='item']//div[@class='info']//div[@class='bd']//div[@class='star']//span[4]/text()").extract_first()
            douban_item['describe'] = item.xpath(".//div[@class='item']//div[@class='info']//div[@class='bd']//p[@class='quote']//span[@class='inq']/text()").extract_first()

            #print(douban_item)  #测试从url所得数据 是否正确
            yield douban_item    #将数据 yield到管道里，然后进行数据的清洗，存储登操作

        # 在for循环外，加一个下页自动跳转。
        # 解析下一页规则，取后一页的xpath
        next_link = response.xpath("//span[@class='next']/link/@href").extract()
        if next_link:
            next_link = next_link[0]
            yield scrapy.Request("https://movie.douban.com/top250" + next_link,callback=self.parse)