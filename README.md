基于[Scrapy](https://scrapy.org/ "scrapy官网")框架的网络爬虫系统
===


### 项目部署说明
- [环境配置](#环境配置)
- [项目部署](#项目部署)
- [项目管理](#项目管理)
- [爬虫启动指令](#爬虫启动指令)
- [Linux系统定时任务](#Linux系统定时任务)
- [其他问题](#其他问题)
- [爬虫创建](#爬虫创建)


### 环境配置
Python虚拟环境配置
Python3.6.5+
```Bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

CentOS7.5 浏览器安装配置(7系列系统安装方式一致)
```Bash
# Firefox
yum install xorg-x11-server-Xvfb bzip gtk3 -y
wget https://download-ssl.firefox.com.cn/releases/firefox/66.0/en-US/Firefox-latest-x86_64.tar.bz2
wget https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux64.tar.gz
tar -jxvf Firefox-latest-x86_64.tar.bz2 -C /opt/software/
tar -zxvf geckodriver-v0.24.0-linux64.tar.gz -C /opt/software/
echo "#!/bin/bash" > /etc/profile.d/firefox.sh
echo "export PATH=\$PATH:/opt/software/firefox" >> /etc/profile.d/firefox.sh

# PhantomJS
wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2
tar -jxvf phantomjs-2.1.1-linux-x86_64.tar.bz2 -C /opt/software/
echo "#!/bin/bash" > /etc/profile.d/phantomjs.sh
echo "export PATH=\$PATH:/opt/software/phantomjs-2.1.1-linux-x86_64/bin" >> /etc/profile.d/phantomjs.sh
```

Ubuntu18.04 浏览器安装配置
```Bash
# Firefox
apt-get install libgtk-3-dev -y
apt-get install xvfb -y
apt-get install libdbus-glib-1-2 -y
wget https://download-ssl.firefox.com.cn/releases/firefox/66.0/en-US/Firefox-latest-x86_64.tar.bz2
wget https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux64.tar.gz
tar -jxvf Firefox-latest-x86_64.tar.bz2 -C /opt/software/
tar -zxvf geckodriver-v0.24.0-linux64.tar.gz -C /opt/software/
echo "#!/bin/bash" > /etc/profile.d/firefox.sh
echo "export PATH=\$PATH:/opt/software/firefox" >> /etc/profile.d/firefox.sh

# Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
wget http://chromedriver.storage.googleapis.com/2.46/chromedriver_linux64.zip
apt-get install xvfb libxi6 libgconf-2-4 -y
apt-get install -f
dpkg -i google-chrome-stable_current_amd64.deb
unzip chromedriver_linux64.zip -d /usr/bin/
```

Ubuntu18.04 Redis数据库配置
```Bash
apt-get install tcl tcl-dev -y
apt-get install redis-server -y
service redis-server start
```


### 项目部署
修改 `design/settings.py` 文件中的一些路径

修改 `design/config_example.cfg` 为 `.config.cfg` 并修改配置

启动管理服务
```Bash
sh deployment/scrapyd-service.sh start
```

部署爬虫项目至管理工具(生成eggs和dbs)
```Bash
sh deployment/deploy.sh
```


### 项目管理
爬虫管理相关指令
```Bash
# 检查爬虫负载信息
curl http://localhost:6800/daemonstatus.json

# 启动爬虫文件(project=项目名称, spider=爬虫名称, key_words=启动爬虫参数)
curl http://localhost:6800/schedule.json -d project=design -d spider=jd -a key_words=拉杆箱

# 查看当前爬虫版本信息
curl http://localhost:6800/listversions.json?project=design

# 终止爬虫进程
curl http://localhost:6800/cancel.json -d project=design -d job=ae8c423cd05411e88449000c29deb11c

# 查看爬虫项目列表信息
curl http://localhost:6800/listprojects.json

# 查看爬虫项目中爬虫文件列表
curl http://localhost:6800/listspiders.json?project=design

# 查看当前已完成爬虫的信息
curl http://localhost:6800/listjobs.json?project=design|python -m json.tool

# 将爬虫项目从管理工具移除
curl http://localhost:6800/delversion.json -d project=design -d version=1539591444
curl http://localhost:6800/delversion.json -d project=design
```


### Linux系统定时任务
编辑`/etc/crontab`
```Bash
0 11 * * * root curl http://127.0.0.1:6800/schedule.json -d project=design -d spider=jd -d mode=update
```

### 爬虫创建
- 创建爬虫(一般使用网站域名进行命名)
```Bash
scrapy genspider -t basic example 'example.com'
```
- 爬取数据字段设置(design/items.py)
- 爬取的数据处理程序(design/piplines.py)


### 其它
* 电商爬虫相关命令 goods.md 文件
* 电商反爬 design\spiders\shop\电商爬虫.xlsx
* 启动爬虫  scrapy crawl 爬虫名称

> 普通爬虫  
电商爬虫脚本  design\spiders\shop  
招聘网站爬虫脚本 design\spiders\recruit  
工业设计奖项网站爬取脚本 design\spiders\prizes  
工业设计网站爬取脚本 design\spiders\design_web  
工业设计公司网站爬取脚本 design\spiders\design_company  

