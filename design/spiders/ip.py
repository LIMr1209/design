# ip代理检测
import scrapy


class SNSpider(scrapy.Spider):
    name = "ip"
    start_urls = ['https://ip.cn/']

    def parse(self, response):
        print(response.xpath('//div[@class="well"]/p//text()'))
