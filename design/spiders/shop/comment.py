# coding:utf-8
import logging
import json
import random
import re
import time
import requests
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter, ProxyError
import fire
from configparser import ConfigParser, ExtendedInterpolation
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def cookie_to_dic(cookie):
    return {item.split('=')[0]: item.split('=')[1] for item in cookie.split('; ')}


class CommentSpider:
    def __init__(self, logger):
        self.logger = logger
        s = requests.Session()
        s.mount('http://', HTTPAdapter(max_retries=5))  # 重试次数
        s.mount('https://', HTTPAdapter(max_retries=5))
        self.s = s
        # 代理列表
        if tunnel_domain:
            if tunnel_user:
                proxies = {
                    "http": "http://%(user)s:%(pwd)s@%(proxy)s:%(port)s/" % {"user": tunnel_user, "pwd": tunnel_pwd,
                                                                             "proxy": tunnel_domain,
                                                                             "port": tunnel_port},
                    "https": "https://%(user)s:%(pwd)s@%(proxy)s:%(port)s/" % {"user": tunnel_user, "pwd": tunnel_pwd,
                                                                               "proxy": tunnel_domain,
                                                                               "port": tunnel_port}
                }
            else:
                proxies = {
                    "http": "http://%(proxy)s:%(port)s/" % {"proxy": tunnel_domain, "port": tunnel_port},
                    "https": "https://%(proxy)s:%(port)s/" % {"proxy": tunnel_domain, "port": tunnel_port}
                }
        else:
            proxies = {'http': '', 'https': ''}
        self.proxies_list = [proxies]
        # pdd 用户认证列表
        self.pdd_accessToken_list = []
        for i, j in enumerate(pdd_access_token_list):
            self.pdd_accessToken_list.append({
                'AccessToken': j,
                'VerifyAuthToken': pdd_verify_auth_token[i]
            })
        self.time_out = 5
        self.sleep = False
        self.random_sleep_start = 5
        self.random_sleep_end = 10
        self.comment_jd_data_url = 'https://club.jd.com/comment/skuProductPageComments.action?callback=fetchJSON_comment98&productId=%s&score=0&sortType=6&page=%s&pageSize=10&isShadowSku=0&fold=1'  # sortType 6 时间排序, 推荐排序 5
        # 有的商品 当前sku 无评论 切换url
        self.switch = False  # jd
        self.comment_pdd_data_url = 'http://apiv3.yangkeduo.com/reviews/%s/list?&size=20&page=%s&label_id=700000000'  # label_id=700000000 最新
        self.comment_tb_data_url = 'https://rate.taobao.com/feedRateList.htm?auctionNumId=%s&currentPageNum=%s&pageSize=20&orderType=feedbackdate&attribute=&sku=&hasSku=false&folded=0&callback=jsonp_tbcrate_reviews_list'  # orderType sort_weight 推荐排序, feedbackdate 最新排序
        self.comment_tm_data_url = 'https://rate.tmall.com/list_detail_rate.htm?itemId=%s&spuId=972811287&sellerId=2901218787&order=3&currentPage=%s&append=0&content=1&tagId=&posi=&picture=&groupId=&needFold=0&_ksTS=1606704651028_691&callback=jsonp692'
        self.taobao_comment_impression = 'https://rate.tmall.com/listTagClouds.htm?itemId=%s&isAll=true&isInner=true'
        self.comment_save_url = opalus_comment_url

    # 保存评论
    def comment_save(self, out_number, data):
        success = False
        while not success:
            try:
                res = self.s.post(self.comment_save_url, json=data)
                success = True
            except requests.exceptions.RequestException as e:
                time.sleep(10)
                # return {'success': False, 'message': "保存失败", 'out_number': out_number}
        if res.status_code != 200 or res.json()['code']:
            message = res.json()['message']
            return {'success': False, 'message': message, 'out_number': out_number}
        # 重复爬取
        if 'existence_count' in res.json() and res.json()['existence_count'] == len(data):
            return {'success': True, 'message': '重复爬取', 'out_number': out_number}
        return {'success': True, 'message': ''}

    # 终止爬取评论
    def comment_end(self, out_number, goods_url):
        comment = {}
        comment['end'] = 1
        comment['good_url'] = goods_url
        try:
            res = self.s.post(self.comment_save_url, data=comment)
        except requests.exceptions.RequestException as e:
            return {'success': False, 'message': "终止爬取评论失败", 'out_number': out_number}
        return {'success': True}

    def data_handle(self, i):
        if i['site_from'] == 8:
            res = self.data_taobao_handle(i['number'])
        elif i['site_from'] == 9:
            res = self.data_tmall_handle(i['number'])
        elif i['site_from'] == 10:
            res = self.data_pdd_handle(i['number'])
        elif i['site_from'] == 11:
            res = self.data_jd_handle(i['number'])
        else:
            res = '渠道错误'
        return res

    def data_jd_handle(self, out_number):
        comment_page = 0
        cookie_dict = cookie_to_dic(
            'shshshfpa=91c6942d-da14-c2f8-0eb7-c05891ac1e7c-1551683113; shshshfpb=t0ymP5ujCD8z19K3fz6fuBQ%3D%3D; pinId=Wrs6UF9apuPvb2HPPQggXbV9-x-f3wj7; __jdv=122270672|direct|-|none|-|1611887512983; __jdu=2478618123; areaId=1; ipLoc-djd=1-72-55653-0; jwotest_product=99; __jda=122270672.2478618123.1586861605.1612316532.1612748600.78; __jdc=122270672; shshshfp=d4e3ec7f44eab431353b7d638561edc3; 3AB9D23F7A4B3C9B=3EXJLGG4UYPDEDNBOTSXMXQZUVX32SEKWFTXGE46WEWUM2CGLLNEBKCHIPLV3GLD7WU2RZ3UCE5VJKALZLXKCTC66U; shshshsID=85394a74a7d97047a88c583b67474b99_5_1612748653702; __jdb=122270672.5.2478618123|78.1612748600; JSESSIONID=FA599CE56385D7FF5C122737B1CD55E2.s1')
        self.s.cookies = requests.utils.cookiejar_from_dict(cookie_dict, cookiejar=None, overwrite=True)
        # cookies = get_jd_cookie()
        while True:
            proxies = random.choice(self.proxies_list)
            ua = UserAgent().random
            headers = {
                'Referer': 'https://item.jd.com/%s.html' % out_number,
                'User-Agent': ua,
            }
            # if comment_res:
            #     headers['Cookie'] = comment_res.headers.get('set-cookie')[1]
            url = self.comment_jd_data_url % (out_number, comment_page)
            try:
                comment_res = self.s.get(url, headers=headers, proxies=proxies, verify=False, timeout=self.time_out)
            except ProxyError as e:
                self.logger.error('代理错误')
                time.sleep(5)
                continue
                # return {'success': False, 'message': "代理错误", 'out_number': out_number, 'page': comment_page}
            except requests.exceptions.RequestException as e:
                self.logger.error('请求错误')
                time.sleep(5)
                continue
                # return {'success': False, 'message': "反爬限制", 'out_number': out_number, 'page': comment_page}
            # 54 好评 3 2 中评 1 差评
            self.s.cookies.set('JSESSIONID', comment_res.cookies.get('JSESSIONID'))
            rex = re.compile('({.*})')
            try:
                result = json.loads(rex.findall(comment_res.text)[0])
            except:
                self.logger.error('json load 错误')
                time.sleep(5)
                continue
                # cookies = get_jd_cookie()
                # return {'success': False, 'message': "反爬限制", 'out_number': out_number, 'page': comment_page}
            if comment_page == 0 and not result['comments'] and not self.switch:
                self.comment_jd_data_url = 'https://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98&productId=%s&score=0&sortType=6&page=%s&pageSize=10&isShadowSku=0&fold=1'
                self.switch = True
                continue
            if not result:
                # cookies = get_jd_cookie()
                time.sleep(5)
                continue
                # return {'success': False, 'message': "反爬限制", 'out_number': out_number, 'page': comment_page}
            data = []
            if 'comments' in result:
                for i in result['comments']:
                    comment = {}
                    comment['positive_review'] = result['productCommentSummary']['goodCount']
                    comment['comment_count'] = result['productCommentSummary']['commentCount']
                    impression = ''
                    for j in result['hotCommentTagStatistics']:
                        impression += j['name'] + '(' + str(j['count']) + ')  '

                    img_urls = []
                    if 'images' in i:
                        for j in i['images']:
                            img_urls.append('https:' + j['imgUrl'].replace('s128x96_jfs', 's616x405_jfs'))
                    comment['images'] = ','.join(img_urls)
                    comment['love_count'] = i['usefulVoteCount']
                    comment['reply_count'] = i['replyCount']
                    comment['score'] = i['score']
                    if i['score'] in [4, 5]:
                        comment['type'] = 0
                    elif i['score'] in [3, 2]:
                        comment['type'] = 2
                    elif i['score'] in [1]:
                        comment['type'] = 1
                    comment['impression'] = impression
                    comment['site_from'] = 11
                    comment['good_url'] = headers['Referer']
                    if i['content'] == '此用户没有填写评论!':
                        comment['first'] = ''
                    elif i['content'] == '评价方未及时做出评价,系统默认好评!':
                        comment['first'] = ''
                    else:
                        comment['first'] = i['content']
                    if 'afterUserComment' in i and i['afterUserComment']:
                        comment['add'] = i['afterUserComment']['content']
                    comment['buyer'] = i['nickname']
                    comment['style'] = i['productColor'] if 'productColor' in i else ''
                    comment['date'] = i['creationTime']
                    data.append(comment)
            if data:
                # data = json.dumps(data, ensure_ascii=False)
                res = self.comment_save(out_number, data)
                if not res['success']:
                    return res
                if res['message'] == '重复爬取':
                    return {'success': True, 'message': "重复爬取", 'out_number': out_number}
                print("保存成功京东", comment_page, out_number)
            pages = result['maxPage']
            if comment_page >= pages or not result['comments']:
                # self.comment_end(out_number, headers['Referer'])
                return {'success': True, 'message': "爬取完成", 'out_number': out_number}
            num = random.randint(self.random_sleep_start, self.random_sleep_end)
            if self.sleep:
                time.sleep(num)
            comment_page += 1

    def data_pdd_handle(self, out_number):
        comment_page = 1
        goods_url = 'http://yangkeduo.com/goods.html?goods_id=%s' % out_number
        while True:
            # proxies = random.choice(self.proxies_list)
            ua = UserAgent().random
            token = random.choice(self.pdd_accessToken_list)
            headers = {
                'Referer': 'http://yangkeduo.com/goods_comments.html?goods_id=%s' % out_number,
                'User-Agent': ua,
                'AccessToken': token['AccessToken'],
                'VerifyAuthToken': token['VerifyAuthToken'],
            }
            url = self.comment_pdd_data_url % (out_number, comment_page)

            try:
                comment_res = self.s.get(url, headers=headers, verify=False, timeout=self.time_out)
            except ProxyError as e:
                self.logger.error('代理错误')
                time.sleep(5)
                continue
                # return {'success': False, 'message': "代理错误", 'out_number': out_number, 'page': comment_page}
            except requests.exceptions.RequestException as e:
                self.logger.error('请求未响应')
                time.sleep(5)
                continue
                # return {'success': False, 'message': "反爬限制", 'out_number': out_number}
            try:
                result = json.loads(comment_res.content)
            except:
                time.sleep(5)
                continue
            if 'error_msg' in result and result['error_msg']:
                return {'success': False, 'message': result['error_msg'], 'out_number': out_number,
                        'page': comment_page}
            if 'empty_comment_text' not in result:
                return {'success': False, 'message': "反爬限制", 'out_number': out_number}
            data = []
            for i in result['data']:
                comment = {}
                img_urls = []
                if 'pictures' in i:
                    for j in i['pictures']:
                        img_urls.append(j['url'])
                comment['images'] = ','.join(img_urls)
                comment['love_count'] = i['favor_count']
                if 'reply_count' in i:
                    comment['reply_count'] = i['reply_count']
                if 'comprehensive_dsr' in i:
                    comment['score'] = i['comprehensive_dsr']
                try:
                    if i['comprehensive_dsr'] < 3:
                        comment['type'] = 1
                    elif i['comprehensive_dsr'] == 3:
                        comment['type'] = 2
                    else:
                        comment['type'] = 0
                except:
                    if i['desc_score'] < 3:
                        comment['type'] = 1
                    elif i['desc_score'] == 3:
                        comment['type'] = 2
                    else:
                        comment['type'] = 0
                comment['good_url'] = goods_url
                if i['comment'] != "此用户未填写文字评论":
                    comment['first'] = i['comment']
                if 'append' in i and i['append']:
                    comment['add'] = i['append']['comment']
                comment['buyer'] = i['name']
                comment['site_from'] = 10
                if i['specs']:
                    style = json.loads(i['specs'])
                    if style:
                        style_str = style[0]['spec_key'] + ":" + style[0]['spec_value']
                        comment['style'] = style_str
                if i['time']:
                    timeArray = time.localtime(i['time'])
                    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                    comment['date'] = otherStyleTime
                data.append(comment)
            if data:
                # data = json.dumps(data, ensure_ascii=False)
                res = self.comment_save(out_number, data)
                if not res['success']:
                    return res
                # if res['message'] == '重复爬取':
                #     return {'success': True, 'message': "重复爬取", 'out_number': out_number}
                print("保存成功拼多多", comment_page, out_number)
            if not result['data']:
                self.comment_end(out_number, goods_url)
                return {'success': True, 'message': "爬取成功", 'out_number': out_number}
            num = random.randint(self.random_sleep_start, self.random_sleep_end)
            time.sleep(random.randint(5, 8))
            # if self.sleep:
            #     time.sleep(num)
            comment_page += 1

    def data_tmall_handle(self, out_number):
        comment_page = 1
        while True:
            res = self.get_taobao_impression(out_number, 9)
            if res['success']:
                impression = res['impression']
                break
            time.sleep(5)
        while True:
            proxies = random.choice(self.proxies_list)
            ua = UserAgent().random
            headers = {
                'Referer': 'https://detail.tmall.com/item.htm?id=%s' % out_number,
                'User-Agent': ua,
                'Cookie': '_bl_uid=vjkhyfh1kL3up48m99pCr7FrpXtk; _m_h5_tk=a4901680887df4de35e80eca7db44b84_1606823592784; _m_h5_tk_enc=9bc810f0923b6d2ffa1255ef0eb10aee; t=4c621df8e85d4fe9067ccde6f510e986; cookie2=19f934d02e95023c00ef6f6c16247b20; _tb_token_=538f3e759d683; _samesite_flag_=true; xlly_s=1; enc=8VjKAvR5cUAIjOxlCLOZcKJvrc68jolYx%2B%2BXKZSjT9%2FFz8LyOvCmZRJkDd6PtDwSKarI7PYNAY8Xh0A58XSpGw%3D%3D; thw=cn; hng=CN%7Czh-CN%7CCNY%7C156; mt=ci=0_0; tracknick=; uc1=cookie14=Uoe0az6%2FCczAvQ%3D%3D; cna=zasMF12t3zoCATzCuQKpN3kO; v=0; x5sec=7b22726174656d616e616765723b32223a226536393430633233383332336665616466656166333533376635366463646233434c76446d50344645497165377565426c734f453767453d227d; l=eBjqXoucQKR1C6x3BO5aourza779rLAXhsPzaNbMiIncC6pCdopMGYxQKOsKgCtRR8XAMTLB4mWKOPytfF1gJs8X7w3xU-CtloD2B; tfstk=cyklBRcOcbP7_BVm1LwSjSvcCLyhC8Tzzvk-3xwwcEPL8GLYV75cWs5ZriK0u4DdO; isg=BC0t6dP2Dkp6levKmUHve7J9PMmnimFctAAvaW84I0aR5kOYN9gnLBbw0LoA5nkU'
            }
            url = self.comment_tm_data_url % (out_number, comment_page)

            try:
                comment_res = self.s.get(url, headers=headers, proxies=proxies, verify=False, timeout=self.time_out)
            except ProxyError as e:
                self.logger.error('代理错误')
                time.sleep(5)
                continue
                # return {'success': False, 'message': "代理错误", 'out_number': out_number, 'page': comment_page}
            except requests.exceptions.RequestException as e:
                self.logger.warning('请求未响应')
                time.sleep(5)
                continue
                # return {'success': False, 'message': "反爬限制", 'out_number': out_number, 'page': comment_page}
            rex = re.compile('({.*})')
            try:
                result = json.loads(rex.findall(comment_res.content.decode('utf-8'))[0])
            except:
                self.logger.warning('json load 错误')
                time.sleep(5)
                continue
            data = []
            if not 'rateDetail' in result or not result['rateDetail']:
                self.logger.warning('反爬限制')
                time.sleep(10)
                continue
            for i in result['rateDetail']['rateList']:
                comment = {}
                comment['impression'] = impression
                comment['type'] = 1 if i['anony'] else 0
                comment['good_url'] = headers['Referer']
                comment['site_from'] = 9
                images = []
                if 'pics' in i:
                    for j in i['pics']:
                        images.append('https:' + j)
                comment['images'] = ','.join(images)
                if i['rateContent'] == '此用户没有填写评论!':
                    comment['first'] = ''
                else:
                    comment['first'] = i['rateContent']
                comment['add'] = i['appendComment']['content'] if i['appendComment'] else ''
                comment['buyer'] = i['displayUserNick']
                comment['style'] = i['auctionSku']
                comment['date'] = i['rateDate']
                data.append(comment)
            if data:
                # data = json.dumps(data, ensure_ascii=False)
                res = self.comment_save(out_number, data)
                if not res['success']:
                    return res
                if res['message'] == '重复爬取':
                    return {'success': True, 'message': "重复爬取", 'out_number': out_number}
                print("保存成功天猫", comment_page, out_number)
            pages = result['rateDetail']['paginator']['lastPage']
            if comment_page >= pages:
                # self.comment_end(out_number, headers['Referer'])
                return {'success': True, 'message': "爬取成功", 'out_number': out_number}
            num = random.randint(self.random_sleep_start, self.random_sleep_end)
            if self.sleep:
                time.sleep(num)
            comment_page += 1

    def data_taobao_handle(self, out_number):
        comment_page = 1
        while True:
            res = self.get_taobao_impression(out_number, 8)
            if res['success']:
                impression = res['impression']
                break
            time.sleep(5)
        while True:
            proxies = random.choice(self.proxies_list)
            ua = UserAgent().random
            headers = {
                'Referer': 'https://item.taobao.com/item.htm?id=' + out_number,
                'User-Agent': ua,
                'Cookie': '_bl_uid=vjkhyfh1kL3up48m99pCr7FrpXtk; _m_h5_tk=a4901680887df4de35e80eca7db44b84_1606823592784; _m_h5_tk_enc=9bc810f0923b6d2ffa1255ef0eb10aee; t=4c621df8e85d4fe9067ccde6f510e986; cookie2=19f934d02e95023c00ef6f6c16247b20; _tb_token_=538f3e759d683; _samesite_flag_=true; xlly_s=1; enc=8VjKAvR5cUAIjOxlCLOZcKJvrc68jolYx%2B%2BXKZSjT9%2FFz8LyOvCmZRJkDd6PtDwSKarI7PYNAY8Xh0A58XSpGw%3D%3D; thw=cn; hng=CN%7Czh-CN%7CCNY%7C156; mt=ci=0_0; tracknick=; uc1=cookie14=Uoe0az6%2FCczAvQ%3D%3D; cna=zasMF12t3zoCATzCuQKpN3kO; v=0; x5sec=7b22726174656d616e616765723b32223a226536393430633233383332336665616466656166333533376635366463646233434c76446d50344645497165377565426c734f453767453d227d; l=eBjqXoucQKR1C6x3BO5aourza779rLAXhsPzaNbMiIncC6pCdopMGYxQKOsKgCtRR8XAMTLB4mWKOPytfF1gJs8X7w3xU-CtloD2B; tfstk=cyklBRcOcbP7_BVm1LwSjSvcCLyhC8Tzzvk-3xwwcEPL8GLYV75cWs5ZriK0u4DdO; isg=BC0t6dP2Dkp6levKmUHve7J9PMmnimFctAAvaW84I0aR5kOYN9gnLBbw0LoA5nkU'
            }
            url = self.comment_tb_data_url % (out_number, comment_page)

            try:
                comment_res = self.s.get(url, headers=headers, proxies=proxies, verify=False, timeout=self.time_out)
            except ProxyError as e:
                self.logger.error('代理错误')
                time.sleep(5)
                continue
                # return {'success': False, 'message': "代理错误", 'out_number': out_number, 'page': comment_page}
            except requests.exceptions.RequestException as e:
                self.logger.warning('请求未响应')
                time.sleep(5)
                continue
                # return {'success': False, 'message': "反爬限制", 'out_number': out_number, 'page': comment_page}
            rex = re.compile('({.*})')
            try:
                result = json.loads(rex.findall(comment_res.content.decode('utf-8'))[0])
            except:
                self.logger.warning('json load 错误')
                time.sleep(5)
                continue
            data = []
            if not 'comments' in result:
                self.logger.warning('反爬限制')
                time.sleep(5)
                continue
            if result['comments']:
                for i in result['comments']:
                    comment = {}
                    if i['rate'] == "1":
                        comment['type'] = 0
                    elif i['rate'] == "0":
                        comment['type'] = 2
                    elif i['rate'] == "-1":
                        comment['type'] = 1
                    images = []
                    if 'photos' in i:
                        for j in i['photos']:
                            images.append('https:' + j['url'])
                    comment['images'] = ','.join(images)
                    comment['love_count'] = i['useful'] if 'useful' in i else 0
                    comment['impression'] = impression
                    comment['good_url'] = headers['Referer']
                    comment['site_from'] = 8
                    if i['content'] == '此用户没有填写评论!' or i['content'] == '此用户没有填写评价。':
                        comment['first'] = ''
                    elif i['content'] == '评价方未及时做出评价,系统默认好评!':
                        comment['first'] = ''
                    else:
                        comment['first'] = i['content']
                    comment['add'] = i['append']['content'] if i['append'] else ''
                    comment['buyer'] = i['user']['nick']
                    comment['style'] = i['auction']['sku']
                    comment['date'] = i['date'].replace('年', '-').replace('月', '-').replace('日', '')
                    data.append(comment)
            if data:
                # data = json.dumps(data, ensure_ascii=False)
                res = self.comment_save(out_number, data)
                if not res['success']:
                    return res
                if res['message'] == '重复爬取':
                    return {'success': True, 'message': "重复爬取", 'out_number': out_number}
                print("保存成功淘宝", comment_page, out_number)
            pages = result['maxPage']
            if comment_page >= pages or not result['maxPage']:
                # self.comment_end(out_number, headers['Referer'])
                return {'success': True, 'message': "爬取成功", 'out_number': out_number}
            num = random.randint(self.random_sleep_start, self.random_sleep_end)
            if self.sleep:
                time.sleep(num)
            comment_page += 1

    def get_taobao_impression(self, out_number, site_from):
        proxies = random.choice(self.proxies_list)
        ua = UserAgent().random
        headers = {
            'Referer': 'https://detail.tmall.com/item.htm?id=%s' % out_number if site_from == 9 else 'https://item.taobao.com/item.htm?&id=' + out_number,
            'User-Agent': ua,
            'Cookie': '_bl_uid=vjkhyfh1kL3up48m99pCr7FrpXtk; _m_h5_tk=a4901680887df4de35e80eca7db44b84_1606823592784; _m_h5_tk_enc=9bc810f0923b6d2ffa1255ef0eb10aee; t=4c621df8e85d4fe9067ccde6f510e986; cookie2=19f934d02e95023c00ef6f6c16247b20; _tb_token_=538f3e759d683; _samesite_flag_=true; xlly_s=1; enc=8VjKAvR5cUAIjOxlCLOZcKJvrc68jolYx%2B%2BXKZSjT9%2FFz8LyOvCmZRJkDd6PtDwSKarI7PYNAY8Xh0A58XSpGw%3D%3D; thw=cn; hng=CN%7Czh-CN%7CCNY%7C156; mt=ci=0_0; tracknick=; uc1=cookie14=Uoe0az6%2FCczAvQ%3D%3D; cna=zasMF12t3zoCATzCuQKpN3kO; v=0; x5sec=7b22726174656d616e616765723b32223a226536393430633233383332336665616466656166333533376635366463646233434c76446d50344645497165377565426c734f453767453d227d; l=eBjqXoucQKR1C6x3BO5aourza779rLAXhsPzaNbMiIncC6pCdopMGYxQKOsKgCtRR8XAMTLB4mWKOPytfF1gJs8X7w3xU-CtloD2B; tfstk=cyklBRcOcbP7_BVm1LwSjSvcCLyhC8Tzzvk-3xwwcEPL8GLYV75cWs5ZriK0u4DdO; isg=BC0t6dP2Dkp6levKmUHve7J9PMmnimFctAAvaW84I0aR5kOYN9gnLBbw0LoA5nkU'
        }
        try:
            impression_res = self.s.get(self.taobao_comment_impression % out_number, headers=headers, proxies=proxies,
                                        verify=False, timeout=self.time_out)
        except ProxyError as e:
            self.logger.error('代理错误')
            return {'success': False, 'message': "代理错误", 'out_number': out_number}
        except requests.exceptions.RequestException as e:
            self.logger.warning('请求未响应')
            return {'success': False, 'message': "请求未响应", 'out_number': out_number}
        rex = re.compile('({.*})')
        impression_data = json.loads(rex.findall(impression_res.content.decode('utf-8'))[0])
        impression = ''
        if not "tags" in impression_data:
            return {'success': False, 'message': "反爬", 'out_number': out_number}
        for i in impression_data['tags']['tagClouds']:
            impression += i['tag'] + '(' + str(i['count']) + ')  '
        return {'success': True, 'impression': impression}


def comment_spider(name, category, reverse=0):
    if category == 'all':
        params = {'category': ''}
    else:
        params = {'category': category}
    if name == 'jd':
        params['site_from'] = 11
    elif name == 'pdd':
        if len(pdd_verify_auth_token) != len(pdd_verify_auth_token):
            print('pdd用户信息长度不匹配')
            return
        params['site_from'] = 10
    elif name == 'tmall':
        params['site_from'] = 9
    elif name == 'taobao':
        params['site_from'] = 8
    else:
        params['site_from'] = ''
    log_file = os.path.abspath(os.path.join(basedir, "..", '..', '..', 'log', "{}_comment.log".format(name)))

    logger = logging.getLogger()
    fh = logging.FileHandler(log_file, encoding="utf-8", mode="a")
    formatter = logging.Formatter("%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.setLevel(logging.DEBUG)
    # while True:
    res = get_goods_data(opalus_goods_comment_url, params, logger, reverse)
        # if not res['success']:
        # break


def get_goods_data(url, params, logger, reverse):
    page = 1
    params['reverse'] = reverse
    while True:
        params['page'] = page
        res = requests.get(opalus_goods_comment_url, params=params, verify=False)
        res = json.loads(res.content)
        spider = CommentSpider(logger)
        for i in res['data']:
            result = spider.data_handle(i)
            print(result)
            if not result['success']:
                return result
        if not res['data']:
            break
        page += 1
    return {'success': True, 'message': ''}


# 浏览器重新获取cookie 提供jd 评论爬取
def get_jd_cookie():
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    # 初始化chrome对象
    browser = webdriver.Chrome(options=chrome_options)
    old_num = len(browser.window_handles)
    js = 'window.open("https://item.jd.com/64144461545.html");'
    browser.execute_script(js)
    browser.switch_to_window(browser.window_handles[old_num])  # 切换新窗口
    browser.delete_all_cookies()
    browser.refresh()
    cookies = browser.get_cookies()
    cookies = [i['name'] + "=" + i['value'] for i in cookies]
    cookies = '; '.join(cookies)
    return cookies


if __name__ == '__main__':
    import urllib3

    urllib3.disable_warnings()
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    basedir = os.path.abspath(os.path.dirname(__file__))

    cf = ConfigParser(interpolation=ExtendedInterpolation())
    filename = os.path.abspath(os.path.join(basedir, "..", '..', '..', ".env"))
    cf.read(filename, encoding="utf-8")

    tunnel_domain = cf.get('proxies', 'tunnel_domain', fallback='')
    tunnel_port = cf.get('proxies', 'tunnel_port', fallback='')
    tunnel_user = cf.get('proxies', 'tunnel_user', fallback='')
    tunnel_pwd = cf.get('proxies', 'tunnel_pwd', fallback='')
    opalus_comment_url = cf.get('api', 'opalus_comment_url')
    opalus_goods_comment_url = cf.get('api', 'opalus_goods_comment_url')
    product_save_url = cf.get('api', 'product_save_url')
    pdd_access_token_list = cf.get('pdd_user', 'access_token_list').split('\n')
    pdd_verify_auth_token = cf.get('pdd_user', 'verify_auth_token').split('\n')
    fire.Fire(comment_spider)
