import json
import scrapy
from design.items import DesignItem

data = {
    'channel': 'redstaraward',
    'evt': 3,
    'open': 0
}


class DesignCaseSpider(scrapy.Spider):
    name = 'redstar'
    allowed_domains = ['bm.redstaraward.org']
    group_id = '1282498772722515968'
    num = 0

    url = 'https://bm.redstaraward.org/redstaraward/doRunT.action?handler=ExpertReviewAction.switchGroup&next=next&formData.groupId=1282498772722515968&start=0&reviewStatus=close'
    cookie = {
        'JSESSIONID': '4A5BE7BA0AC0EA34729330D19C90A25C',
        'SWORDLITE_POSTID': 'BE966T1E7GHLEUQFHURD522J'
    }

    def start_requests(self):
        yield scrapy.Request(self.url, cookies=self.cookie, dont_filter=True)

    def parse(self, response):
        product_id_list = response.xpath('//img[@class="productsPic"]/@productid').extract()
        group_id_list = response.xpath('//img[@class="productsPic"]/@groupid').extract()
        zid_list = response.xpath('//img[@class="productsPic"]/@zid').extract()
        title_list = response.xpath('//p[@class="productTitle"]/text()').extract()
        for i, j in enumerate(product_id_list):
            item = DesignItem()
            item['title'] = title_list[i]
            item[
                'url'] = 'https://bm.redstaraward.org/redstaraward/doRunT.action?handler=ExpertReviewAction.toReview&formData.groupId=%s&formData.productId=%s&formData.zid=%s&isView=view&start=0&reviewStatus=close' % (
                group_id_list[i], j, zid_list[i])
            FormData = {'groupId': group_id_list[i], 'productId': j, 'zid': zid_list[i]}
            yield scrapy.FormRequest(
                url='https://bm.redstaraward.org/redstaraward/doRunT.action?handler=ExpertReviewAction.ajaxProductInfo',
                callback=self.parse_detail, formdata=FormData, cookies=self.cookie, meta={'item': item})

        if self.num < 869:
            self.num += 10
            yield scrapy.Request(
                url="https://bm.redstaraward.org/redstaraward/doRunT.action?handler=ExpertReviewAction.switchGroup&next=next&formData.groupId=1282498772722515968&start=%s&reviewStatus=close" % self.num,
                callback=self.parse, cookies=self.cookie, dont_filter=True)

    def parse_detail(self, response):
        item = response.meta['item']
        res = json.loads(response.text)
        productInnovationZh = res['introInfo']['productInnovationZh']  # 创新性
        productUtilityZh = res['introInfo']['productUtilityZh']  # 实用性
        productEconZh = res['introInfo']['productEconZh']  # 经济性
        productEnvirZh = res['introInfo']['productEnvirZh']  # 环保性
        productCraftZh = res['introInfo']['productCraftZh']  # 工艺性
        productAesthZh = res['introInfo']['productAesthZh']  # 美观性
        content = '创新性：%s\n实用性：%s\n经济性：%s\n环保性：%s\n工艺性：%s\n美观性：%s' % (
            productInnovationZh, productUtilityZh, productEconZh, productEnvirZh, productCraftZh, productAesthZh)
        img_ids = res['imgIdList']
        img_urls = []
        for i in img_ids:
            img_urls.append(
                'https://bm.redstaraward.org/redstaraward/doRunT.action?handler=ExpertReviewAction.mainShowImage&productId=%s' % i)
        item['img_urls'] = ','.join(img_urls)
        item['remark'] = content
        for key, value in data.items():
            item[key] = value

        yield scrapy.Request(url=item['url'], callback=self.parse_other, cookies=self.cookie, dont_filter=True,
                             meta={'item': item})

    def parse_other(self, response):
        item = response.meta['item']
        item['tags'] = response.xpath('//*[@id="productType"]/text()').extract()[0]
        date = response.xpath('//*[@id="date"]/text()').extract()[0]
        weight = response.xpath('//*[@id="weight"]/text()').extract()[0]
        lwg = response.xpath('//*[@id="lwg"]/text()').extract()[0]
        desc = '上市时间：%s\n尺寸长*宽*高(L*W*H)单位：厘米(cm)：%s\n重量单位：千克(kg)：%s\n' % (date, lwg, weight)
        item['remark'] = desc + item['remark']
        return item
