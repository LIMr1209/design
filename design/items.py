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
    description = scrapy.Field()  # 前台描述
    color_tags = scrapy.Field()  # 颜色标签
    brand_tags = scrapy.Field()  # 品牌标签
    material_tags = scrapy.Field()  # 材质
    style_tags = scrapy.Field()  # 风格
    technique_tags = scrapy.Field()  # 工艺
    other_tags = scrapy.Field()  # 其它
    customer = scrapy.Field()  # 客户
    company = scrapy.Field()  # 公司
    user_id = scrapy.Field()  # 用户ID  0
    kind = scrapy.Field()  # 类型:  1
    brand_id = scrapy.Field()  # 品牌ID 0
    prize = scrapy.Field()  # 奖项
    category_id = scrapy.Field()  # 分类ID 0
    designer = scrapy.Field()  # 设计师
    status = scrapy.Field()  # 状态: 0.禁用；1.启用
    open = scrapy.Field()  # 公开
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
    channel = scrapy.Field()


class CompanyItem(scrapy.Item):
    # 基本信息
    name = scrapy.Field()  # 企业全称	NULL
    short_name = scrapy.Field()  # 企业简称	NULL
    url = scrapy.Field()  # 官网地址	NULL
    logo_url = scrapy.Field()  # LOGO地址	NULL
    scale_label = scrapy.Field()  # 规模	NULL		如：50-100人
    nature_label = scrapy.Field()  # 性质	NULL		如：国企、私企
    management_model = scrapy.Field()  # 经营模式	NULL
    scope_business = scrapy.Field()  # 经营范围、主营业务	NULL
    advantage = scrapy.Field()  # 优势、亮点	NULL
    description = scrapy.Field()  # 简述	NULL
    branch = scrapy.Field()  # 分公司数量	NULL
    wx_public_no = scrapy.Field()  # 微信公号ID	NULL
    wx_public = scrapy.Field()  # 微信公号名称	NULL
    wx_public_qr = scrapy.Field()  # 微信公号二维码地址	NULL
    remark = scrapy.Field()  # 人工备注	NULL
    tags = scrapy.Field()  # 标签	NULL		多个用','分隔
    is_high_tech = scrapy.Field()  # 高新企业	NULL		是否是高新企业：0否；1.是；
    company_status_label = scrapy.Field()  # 公司状态	NULL

    # 联系人信息
    province = scrapy.Field()  # 所在省份	NULL
    city = scrapy.Field()  # 所在城市	NULL
    address = scrapy.Field()  # 详细地址	NULL
    zip_code = scrapy.Field()  # 邮编	NULL
    contact_name = scrapy.Field()  # 联系人姓名	NULL
    contact_phone = scrapy.Field()  # 联系人手机	NULL
    contact_email = scrapy.Field()  # 联系人邮箱	NULL
    contact_wx = scrapy.Field()  # 微信	NULL
    contact_qq = scrapy.Field()  # 联系人QQ	NULL
    sex = scrapy.Field()  # 性别	0		0.默认；1.男；2.女；
    tel = scrapy.Field()  # 电话	NULL
    s_contact_name = scrapy.Field()  # 销售姓名	NULL
    s_contact_phone = scrapy.Field()  # 销售手机	NULL
    s_contact_email = scrapy.Field()  # 销售邮箱	NULL
    s_contact_wx = scrapy.Field()  # 销售微信	NULL
    s_sex = scrapy.Field()  # 销售性别	0		0.默认；1.男；2.女；
    s_tel = scrapy.Field()  # 销售电话	NULL
    s_contact_qq = scrapy.Field()  # 销售QQ	NULL

    # 公司注册信息
    founder = scrapy.Field()  # 创始人	NULL
    founder_desc = scrapy.Field()  # 创始人介绍	NULL
    registered_capital = scrapy.Field()  # 注册资金	NULL
    registered_time = scrapy.Field()  # 注册时间	NULL
    company_count = scrapy.Field()  # 法人公司数量	NULL
    company_type = scrapy.Field()  # 公司类型	NULL		如：有限责任公司
    registration_number = scrapy.Field()  # 工商注册号	NULL
    credit_code = scrapy.Field()  # 统一信用代码	NULL
    identification_number = scrapy.Field()  # 纳税人识别号	NULL
    industry = scrapy.Field()  # 行业	NULL
    business_term = scrapy.Field()  # 营业期限	NULL
    issue_date = scrapy.Field()  # 核准日期	NULL
    registration_authority = scrapy.Field()  # 登记机关	NULL
    english_name = scrapy.Field()  # 英文名称	NULL
    registered_address = scrapy.Field()  # 注册地址	NULL
    organization_code = scrapy.Field()  # 组织机构代码	NULL

    # 系统
    craw_user_id = scrapy.Field()  # 负责人ID	NULL	0	1.--；2.TIAN；3.LZB；5.WJP；7.WSH；
    channel = scrapy.Field()  # 获取渠道	NULL
    soure_url = scrapy.Field()  # 来源地址	NULL
    edit_pattern = scrapy.Field()  # 编辑模式	0	0	是否允许编辑：0.关闭；1.开启；


class MeizituItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = scrapy.Field()
    image_urls = scrapy.Field()
    image_paths = scrapy.Field()
    title = scrapy.Field()


class CommentItem(scrapy.Item):
    type = scrapy.Field()  # 品论类型 0 好评 1 差评 2 中评
    first = scrapy.Field()  # 初评
    add = scrapy.Field()  # 追评
    buyer = scrapy.Field()  # 买家
    style = scrapy.Field()  # 样式
    date = scrapy.Field()
    good_url = scrapy.Field()


class TaobaoItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    category = scrapy.Field()
    url = scrapy.Field()  # 链接
    title = scrapy.Field()  # 名称
    original_price = scrapy.Field()  # 原价
    out_number = scrapy.Field()  # 商品站外编号
    shop_id = scrapy.Field()  # 京东商品父id
    img_urls = scrapy.Field()
    sku_ids = scrapy.Field()
    promotion_price = scrapy.Field()  # 优惠价
    price_range = scrapy.Field()  # 价格范围
    sale_count = scrapy.Field()  # 成交量
    favorite_count = scrapy.Field()  # 收藏量
    service = scrapy.Field()  # 服务承诺
    reputation = scrapy.Field()  # 信誉
    detail_sku = scrapy.Field()  # 各规格的商品信息
    detail_str = scrapy.Field()  # 商品详情
    detail_dict = scrapy.Field()
    cover_url = scrapy.Field()  # 图片地址
    impression = scrapy.Field()  # 大家印象
    comment_count = scrapy.Field()
    site_from = scrapy.Field()
    site_type = scrapy.Field()
