import scrapy
from design.items import DesignItem
import re


# 2016 319  2015  309  2014 286 2013 301 2012 277 2011 247 2010 203 2009 100 2008 143 2007 105 2006 19
class DesignCaseSpider(scrapy.Spider):
    name = 'ssyer'
    allowed_domains = ['www.ssyer.com']
    year = 2006
    yearid = '810'
    year_list = {
        '2016': '5452', '2015': '4475', '2014': '3398', '2013': '2653', '2012': '804',
        '2011': '803', '2010': '802', '2009': '807', '2008': '808', '2007': '809', '2006': '810'
    }
    cmd = 'getProList'
    type = 1
    page = 1
    url = 'http://www.redstaraward.org/ajax/AjaxHandler_HXJGW_GW.ashx'
    prize_level = '至尊金奖'
    prize_levels = ['至尊金奖','银奖', '最佳团队奖', '原创奖金奖', '原创奖', '未来之星奖', '金奖', '红星奖', '最佳新人奖', '原创奖银奖', '优秀设计师奖']
    key_id = 0
    total = 1
    def start_requests(self):
        # FormRequest 是Scrapy发送POST请求的方法
        yield scrapy.FormRequest(
            url=self.url,
            formdata={"cmd": self.cmd, "page": str(self.page), "yearid": self.yearid, 'type': str(self.type),
                      'key': self.prize_level},
            callback=self.parse,
            dont_filter=True
        )

    def parse(self, response):

        content = response.body.decode('utf-8')
        rex = re.compile(r'(/content/details.+?html)')
        result = list(set(rex.findall(content)))
        for i in result:
            yield scrapy.Request(url="http://www.redstaraward.org/" + i, callback=self.parse_detail,dont_filter=True)
        if result:
            self.page += 1
            yield scrapy.FormRequest(
                url=self.url,
                formdata={"cmd": self.cmd, "page": str(self.page), "yearid": self.yearid, 'type': str(self.type),
                          'key': self.prize_level},
                callback=self.parse,
                dont_filter=True
            )
        else:
            if self.key_id < len(self.prize_levels)-1:
                self.key_id += 1
                self.page = 1
                self.prize_level = self.prize_levels[self.key_id]
                yield scrapy.FormRequest(
                    url=self.url,
                    formdata={"cmd": self.cmd, "page": str(self.page), "yearid": self.yearid,
                              'type': str(self.type),
                              'key': self.prize_level},
                    callback=self.parse,
                    dont_filter=True
                )
            else:
                if self.year < 2016:
                    self.key_id = 0
                    self.year += 1
                    self.page = 1
                    self.prize_level = self.prize_levels[self.key_id]
                    self.yearid = self.year_list[str(self.year)]
                    yield scrapy.FormRequest(
                        url=self.url,
                        formdata={"cmd": self.cmd, "page": str(self.page), "yearid": self.yearid,
                                  'type': str(self.type),
                                  'key': self.prize_level},
                        callback=self.parse,
                        dont_filter=True
                    )



    def parse_detail(self, response):
        url = response.url
        print(url)
        self.total += 1
        item = DesignItem()
        img_url = response.xpath('//div[@class="only"]/img/@src').extract()[0]
        if not img_url.startswith('http://www.redstaraward.org'):
            img_url = 'http://www.redstaraward.org/' + img_url
        try:
            title = response.xpath('//div[@class="zuopin_h"][1]/div/text()').extract()[0]
        except:
            title = ''
        try:
            designer = response.xpath('//div[@class="zuopin_h"][2]/div/text()').extract()[0]
        except:
            designer = ''
        try:
            company = response.xpath('//div[@class="zuopin_h"][3]/div/text()').extract()[0]
        except:
            company = ''
        try:
            remark = response.xpath('//div[@class="zuopin_h"][6]/div/text()').extract()[0]
            if len(remark) > 450:
                remark = remark[:450]
        except:
            remark = ''
        try:
            prize_level = response.xpath('//div[@class="zuopin_h"][4]/div/text()').extract()[0]
        except:
            prize_level = ''
        item['img_url'] = img_url.strip()
        item['title'] = title.strip()
        item['company'] = company.strip()
        item['prize_time'] = str(self.year)
        item['remark'] = remark.replace('\n','').replace(' ','').replace('\r','').strip()
        item['prize_level'] = prize_level.strip()
        item['designer'] = designer.strip()
        item['url'] = url.strip()
        for key, value in data.items():
            item[key] = value
        print("总数",self.total)
        yield item
