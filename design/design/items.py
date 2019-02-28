# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DesignItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    title = scrapy.Field()  # 标题
    name = scrapy.Field()  # 名称
    channel = scrapy.Field()  # 渠道
    sub_title = scrapy.Field()  # 副标题
    img_urls = scrapy.Field()  # 图片地址
    path = scrapy.Field()  # 七牛路径
    local_name = scrapy.Field()  # 本地文件名称
    local_path = scrapy.Field()  # 本地文件路径
    ext = scrapy.Field()  # 扩展名
    tags = scrapy.Field()  # 标签
    color_tags = scrapy.Field()  # 颜色标签
    brand_tags = scrapy.Field()  # 品牌标签
    material_tags = scrapy.Field()  # 材质
    style_tags = scrapy.Field()  # 风格
    technique_tags = scrapy.Field()  # 工艺
    other_tags = scrapy.Field()  # 其它
    company = scrapy.Field()  # 公司
    user_id = scrapy.Field()  # 用户ID  0
    kind = scrapy.Field()  # 类型:  1
    brand_id = scrapy.Field()  # 品牌ID 0
    prize = scrapy.Field()  # 奖项
    category_id = scrapy.Field()  # 分类ID 0
    designer = scrapy.Field()  # 设计师
    status = scrapy.Field()  # 状态: 0.禁用；1.启用
    remark = scrapy.Field()  # 描述
    info = scrapy.Field()  # 其它json串
    evt = scrapy.Field()  # 来源：1.默认  3.振斌
    deleted = scrapy.Field()  # 是否软删除 0
    created_at = scrapy.Field()  # 创建时间
    updated_at = scrapy.Field()  # 创建时间
    url = scrapy.Field()  # 原文地址


class ProduceItem(scrapy.Item):
    img_urls = scrapy.Field()
    tag = scrapy.Field()
    img_url = scrapy.Field()