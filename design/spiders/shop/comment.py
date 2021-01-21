# coding:utf-8

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


class CommentSpider:
    def __init__(self):
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
                    "https": "http://%(user)s:%(pwd)s@%(proxy)s:%(port)s/" % {"user": tunnel_user, "pwd": tunnel_pwd,
                                                                              "proxy": tunnel_domain,
                                                                              "port": tunnel_port}
                }
            else:
                proxies = {
                    "http": "http://%(proxy)s:%(port)s/" % {"proxy": tunnel_domain, "port": tunnel_port},
                    "https": "http://%(proxy)s:%(port)s/" % {"proxy": tunnel_domain, "port": tunnel_port}
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
        self.sleep = True
        self.random_sleep_start = 2
        self.random_sleep_end = 5
        self.comment_jd_data_url = 'https://club.jd.com/comment/skuProductPageComments.action?callback=fetchJSON_comment98&productId=%s&score=0&sortType=5&page=%s&pageSize=10&isShadowSku=0&fold=1'
        # 有的商品 当前sku 无评论 切换url
        self.switch = False  # jd
        self.comment_pdd_data_url = 'http://yangkeduo.com/proxy/api/reviews/%s/list?pdduid=9575597704&page=%s&size=20&enable_video=1&enable_group_review=1&label_id=0'
        self.comment_tb_data_url = 'https://rate.taobao.com/feedRateList.htm?auctionNumId=%s&currentPageNum=%s&pageSize=20&orderType=sort_weight&attribute=&sku=&hasSku=false&folded=0&callback=jsonp_tbcrate_reviews_list'
        self.comment_tm_data_url = 'https://rate.tmall.com/list_detail_rate.htm?itemId=%s&spuId=972811287&sellerId=2901218787&order=3&currentPage=%s&append=0&content=1&tagId=&posi=&picture=&groupId=&needFold=0&_ksTS=1606704651028_691&callback=jsonp692'
        self.taobao_comment_impression = 'https://rate.tmall.com/listTagClouds.htm?itemId=%s&isAll=true&isInner=true'
        self.comment_save_url = opalus_comment_url

    # 保存评论
    def comment_save(self, out_number, data):
        try:
            res = self.s.post(self.comment_save_url, json=data)
        except requests.exceptions.RequestException as e:
            return {'success': False, 'message': "保存失败", 'out_number': out_number}
        if res.status_code != 200 or res.json()['code']:
            message = res.json()['message']
            return {'success': False, 'message': message, 'out_number': out_number}
        return {'success': True}

    # 终止爬取评论
    def comment_end(self, out_number, headers):
        comment = {}
        comment['end'] = 1
        comment['good_url'] = headers['Referer']
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
        while True:
            proxies = random.choice(self.proxies_list)
            ua = UserAgent().random
            headers = {
                'Referer': 'https://item.jd.com/%s.html' % out_number,
                'User-Agent': ua,
                'Cookie': '__jdv=76161171|direct|-|none|-|1610329405998; __jdu=16103294059961137138561; areaId=1; PCSYCityID=CN_110000_110100_110105; shshshfpa=f09b3217-4001-fc20-58f9-b1c005061b6e-1610329409; shshshfpb=jWqGTcT%2FwcJVlyMzTKm6iqA%3D%3D; __jda=122270672.16103294059961137138561.1610329406.1610329406.1610329406.1; __jdc=122270672; shshshfp=e055c2e13f622066cff2f5f987592135; shshshsID=d88d11986d0b12b7cc570438e210d8f9_3_1610329423064; __jdb=122270672.3.16103294059961137138561|1.1610329406; ipLoc-djd=1-72-55653-0; 3AB9D23F7A4B3C9B=E7MDYEC5EOP32SWZP4FX4FOIZPNTF5NSHBOUS3IOKPFAUDJLD5FWSZSRWQUHEH5UA3DNBXQEWWVPPHK4LXTIDWNONE; JSESSIONID=2B49AF0022B29BD23BF54C54DF4CA76C.s1; jwotest_product=99'
            }
            # if comment_res:
            #     headers['Cookie'] = comment_res.headers.get('set-cookie')[1]
            url = self.comment_jd_data_url % (out_number, comment_page)

            try:
                comment_res = self.s.get(url, headers=headers, proxies=proxies, verify=False, timeout=self.time_out)
            except ProxyError as e:
                return {'success': False, 'message': "代理错误", 'out_number': out_number, 'page': comment_page}
            except requests.exceptions.RequestException as e:
                return {'success': False, 'message': "反爬限制", 'out_number': out_number, 'page': comment_page}
            # 54 好评 3 2 中评 1 差评
            rex = re.compile('({.*})')
            try:
                result = json.loads(rex.findall(comment_res.text)[0])
            except:
                return {'success': False, 'message': "反爬限制", 'out_number': out_number, 'page': comment_page}
            if comment_page == 0 and not result['comments'] and not self.switch:
                self.comment_jd_data_url = 'https://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98&productId=%s&score=0&sortType=5&page=%s&pageSize=10&isShadowSku=0&fold=1'
                self.switch = True
                continue
            if not result:
                return {'success': False, 'message': "反爬限制", 'out_number': out_number, 'page': comment_page}
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
                print("保存成功京东", comment_page, out_number)
            pages = result['maxPage']
            if comment_page >= pages or not result['comments']:
                self.comment_end(out_number, headers)
                return {'success': True, 'message': "爬取完成", 'out_number': out_number}
            num = random.randint(self.random_sleep_start, self.random_sleep_end)
            if self.sleep:
                time.sleep(num)
            comment_page += 1

    def data_pdd_handle(self, out_number):
        comment_page = 1
        while True:
            proxies = random.choice(self.proxies_list)
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
                comment_res = self.s.get(url, headers=headers, proxies=proxies, verify=False, timeout=self.time_out)
            except ProxyError as e:
                return {'success': False, 'message': "代理错误", 'out_number': out_number, 'page': comment_page}
            except requests.exceptions.RequestException as e:
                return {'success': False, 'message': "反爬限制", 'out_number': out_number}
            result = json.loads(comment_res.content)
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
                comment['reply_count'] = i['reply_count']
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
                comment['good_url'] = headers['Referer']
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
                print("保存成功拼多多", comment_page, out_number)
            if not result['data']:
                self.comment_end(out_number, headers)
                return {'success': True, 'message': "爬取成功", 'out_number': out_number}
            num = random.randint(self.random_sleep_start, self.random_sleep_end)
            if self.sleep:
                time.sleep(num)
            comment_page += 1

    def data_tmall_handle(self, out_number):
        comment_page = 1
        proxies = random.choice(self.proxies_list)
        ua = UserAgent().random
        headers = {
            'Referer': 'https://detail.tmall.com/item.htm?id=%s' % out_number,
            'User-Agent': ua,
            'Cookie': '_bl_uid=vjkhyfh1kL3up48m99pCr7FrpXtk; _m_h5_tk=a4901680887df4de35e80eca7db44b84_1606823592784; _m_h5_tk_enc=9bc810f0923b6d2ffa1255ef0eb10aee; t=4c621df8e85d4fe9067ccde6f510e986; cookie2=19f934d02e95023c00ef6f6c16247b20; _tb_token_=538f3e759d683; _samesite_flag_=true; xlly_s=1; enc=8VjKAvR5cUAIjOxlCLOZcKJvrc68jolYx%2B%2BXKZSjT9%2FFz8LyOvCmZRJkDd6PtDwSKarI7PYNAY8Xh0A58XSpGw%3D%3D; thw=cn; hng=CN%7Czh-CN%7CCNY%7C156; mt=ci=0_0; tracknick=; uc1=cookie14=Uoe0az6%2FCczAvQ%3D%3D; cna=zasMF12t3zoCATzCuQKpN3kO; v=0; x5sec=7b22726174656d616e616765723b32223a226536393430633233383332336665616466656166333533376635366463646233434c76446d50344645497165377565426c734f453767453d227d; l=eBjqXoucQKR1C6x3BO5aourza779rLAXhsPzaNbMiIncC6pCdopMGYxQKOsKgCtRR8XAMTLB4mWKOPytfF1gJs8X7w3xU-CtloD2B; tfstk=cyklBRcOcbP7_BVm1LwSjSvcCLyhC8Tzzvk-3xwwcEPL8GLYV75cWs5ZriK0u4DdO; isg=BC0t6dP2Dkp6levKmUHve7J9PMmnimFctAAvaW84I0aR5kOYN9gnLBbw0LoA5nkU'
        }
        try:
            impression_res = self.s.get(self.taobao_comment_impression % out_number, headers=headers, proxies=proxies,
                                        verify=False, timeout=self.time_out)
        except ProxyError as e:
            return {'success': False, 'message': "代理错误", 'out_number': out_number, 'page': comment_page}
        rex = re.compile('({.*})')
        impression_data = json.loads(rex.findall(impression_res.content.decode('utf-8'))[0])
        impression = ''
        for i in impression_data['tags']['tagClouds']:
            impression += i['tag'] + '(' + str(i['count']) + ')  '
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
                return {'success': False, 'message': "代理错误", 'out_number': out_number, 'page': comment_page}
            except requests.exceptions.RequestException as e:
                return {'success': False, 'message': "反爬限制", 'out_number': out_number, 'page': comment_page}
            rex = re.compile('({.*})')
            try:
                result = json.loads(rex.findall(comment_res.content.decode('utf-8'))[0])
            except:
                print(comment_res.content)
                return
            data = []
            if 'rateDetail' in result:
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
                print("保存成功天猫", comment_page, out_number)
            pages = result['rateDetail']['paginator']['lastPage']
            if comment_page >= pages:
                self.comment_end(out_number, headers)
                return {'success': True, 'message': "爬取成功", 'out_number': out_number}
            num = random.randint(self.random_sleep_start, self.random_sleep_end)
            if self.sleep:
                time.sleep(num)
            comment_page += 1

    def data_taobao_handle(self, out_number):
        comment_page = 1
        proxies = random.choice(self.proxies_list)
        ua = UserAgent().random
        headers = {
            'Referer': 'https://item.taobao.com/item.htm?&id=' + out_number,
            'User-Agent': ua,
            'Cookie': '_bl_uid=vjkhyfh1kL3up48m99pCr7FrpXtk; _m_h5_tk=a4901680887df4de35e80eca7db44b84_1606823592784; _m_h5_tk_enc=9bc810f0923b6d2ffa1255ef0eb10aee; t=4c621df8e85d4fe9067ccde6f510e986; cookie2=19f934d02e95023c00ef6f6c16247b20; _tb_token_=538f3e759d683; _samesite_flag_=true; xlly_s=1; enc=8VjKAvR5cUAIjOxlCLOZcKJvrc68jolYx%2B%2BXKZSjT9%2FFz8LyOvCmZRJkDd6PtDwSKarI7PYNAY8Xh0A58XSpGw%3D%3D; thw=cn; hng=CN%7Czh-CN%7CCNY%7C156; mt=ci=0_0; tracknick=; uc1=cookie14=Uoe0az6%2FCczAvQ%3D%3D; cna=zasMF12t3zoCATzCuQKpN3kO; v=0; x5sec=7b22726174656d616e616765723b32223a226536393430633233383332336665616466656166333533376635366463646233434c76446d50344645497165377565426c734f453767453d227d; l=eBjqXoucQKR1C6x3BO5aourza779rLAXhsPzaNbMiIncC6pCdopMGYxQKOsKgCtRR8XAMTLB4mWKOPytfF1gJs8X7w3xU-CtloD2B; tfstk=cyklBRcOcbP7_BVm1LwSjSvcCLyhC8Tzzvk-3xwwcEPL8GLYV75cWs5ZriK0u4DdO; isg=BC0t6dP2Dkp6levKmUHve7J9PMmnimFctAAvaW84I0aR5kOYN9gnLBbw0LoA5nkU'
        }
        try:
            impression_res = self.s.get(self.taobao_comment_impression % out_number, headers=headers, proxies=proxies,
                                        verify=False, timeout=self.time_out)
        except ProxyError as e:
            return {'success': False, 'message': "代理错误", 'out_number': out_number, 'page': comment_page}
        rex = re.compile('({.*})')
        impression_data = json.loads(rex.findall(impression_res.content.decode('utf-8'))[0])
        impression = ''
        for i in impression_data['tags']['tagClouds']:
            impression += i['tag'] + '(' + str(i['count']) + ')  '
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
                return {'success': False, 'message': "代理错误", 'out_number': out_number, 'page': comment_page}
            except requests.exceptions.RequestException as e:
                return {'success': False, 'message': "反爬限制", 'out_number': out_number, 'page': comment_page}
            rex = re.compile('({.*})')
            result = json.loads(rex.findall(comment_res.content.decode('utf-8'))[0])
            data = []
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
                    if i['content'] == '此用户没有填写评论!':
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
                print("保存成功淘宝", comment_page, out_number)
            pages = result['maxPage']
            if comment_page >= pages or not result['maxPage']:
                self.comment_end(out_number, headers)
                return {'success': True, 'message': "爬取成功", 'out_number': out_number}
            num = random.randint(self.random_sleep_start, self.random_sleep_end)
            if self.sleep:
                time.sleep(num)
            comment_page += 1


def comment_spider(name, category):
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
    res = requests.get(opalus_goods_comment_url, params=params, verify=False)
    res = json.loads(res.content)
    spider = CommentSpider()
    for i in res['data']:
        result = spider.data_handle(i)
        print(result)
        if not result['success']:
            break


if __name__ == '__main__':
    import urllib3

    urllib3.disable_warnings()

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
