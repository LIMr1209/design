基于Scrapy+Selenium的电商爬虫系统
===


### 项目部署说明
- [环境配置](#环境配置)
- [项目部署](#项目部署)
- [爬虫启动指令](#爬虫启动指令)


### 环境配置
Python虚拟环境配置
Python3.6.5+
在 https://npm.taobao.org/mirrors/chromedriver/ 下载和chrome 浏览器版本对应的chromedriver 驱动,并设置环境变量
```Bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 项目部署
- 把根目录文件```.env_example```复制到根目录```.env```，并修改相关配置作为当前环境的配置文件  

### 项目管理
爬虫管理相关指令
#### 商品信息
```Bash

```
#### 
全量爬取京东商品的评论
```Bash
python design/spiders/shop/commeny.py jd all  
```
全量爬取淘宝商品的评论
```Bash
python design/spiders/shop/commeny.py taobao all  
```
全量爬取天猫商品的评论
```Bash
python design/spiders/shop/commeny.py tmall all  
```
全量爬取拼多多商品的评论
```Bash
python design/spiders/shop/commeny.py pdd all  
```
指定分类爬取京东商品的评论
```Bash
python design/spiders/shop/commeny.py jd 吹风机  
```
全量爬取京东商品的评论(1，反转待爬取商品列表)
```Bash
python design/spiders/shop/commeny.py jd all 1
```
