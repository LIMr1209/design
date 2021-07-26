# coding:utf-8
import asyncio
import logging
import json
import random
import re
import time

import pyautogui as pyautogui
import requests
from fake_useragent import UserAgent
from pyppeteer import connect
from requests.adapters import HTTPAdapter, ProxyError
import fire
from configparser import ConfigParser, ExtendedInterpolation
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def cookie_to_dict(cookie):
    return {item.split('=')[0]: item.split('=')[1] for item in cookie.split('; ')}


def dict_to_cookie(data):
    cookie = ''
    for key, value in data.items():
        cookie += key + '=' + value + ';'
    cookie = cookie[:-1]
    return cookie


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
        self.comment_tm_data_url = 'https://rate.tmall.com/list_detail_rate.htm?itemId=%s&spuId=972811287&sellerId=2901218787&order=1&currentPage=%s&append=0&content=1&tagId=&posi=&picture=&groupId=&needFold=0&_ksTS=1606704651028_691&callback=jsonp692'
        self.taobao_comment_impression = 'https://rate.tmall.com/listTagClouds.htm?itemId=%s&isAll=true&isInner=true'
        self.comment_save_url = opalus_comment_url

    # 保存评论
    def comment_save(self, out_number, json_data, new_time):
        data = json_data['data']
        success = False
        # data.sort(key=lambda x:x['date'])
        # new_data = []
        # if new_time:
        #     for i in data:
        #         if i['date'] > new_time:
        #             new_data.append(i)
        # else:
        #     new_data = deepcopy(data)
        # if not new_data:
        #     return {'success': True, 'message': '重复爬取', 'out_number': out_number}
        # json_data['data'] = new_data
        while not success:
            try:
                res = self.s.post(self.comment_save_url, json=json_data)
                success = True
            except requests.exceptions.RequestException as e:
                time.sleep(10)
                self.logger.warning('保存评论失败 正在重试')
                # return {'success': False, 'message': "保存失败", 'out_number': out_number}
        if res.status_code != 200 or res.json()['code']:
            message = res.json()['message']
            return {'success': False, 'message': message, 'out_number': out_number}
        # 重复爬取
        if 'existence_count' in res.json() and res.json()['existence_count'] == len(data):
            return {'success': True, 'message': '重复爬取', 'out_number': out_number}
        # if len(new_data) < len(data):
        #     return {'success': True, 'message': '重复爬取', 'out_number': out_number}
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
            res = self.data_taobao_handle(i['number'], i['_id'], i['site_from'], i['new_time'])
        elif i['site_from'] == 9:
            res = self.data_tmall_handle(i['number'], i['_id'], i['site_from'], i['new_time'])
        elif i['site_from'] == 10:
            res = self.data_pdd_handle(i['number'], i['_id'], i['site_from'], i['new_time'])
        elif i['site_from'] == 11:
            res = self.data_jd_handle(i['number'], i['_id'], i['site_from'], i['new_time'])
        else:
            res = '渠道错误'
        return res

    def data_jd_handle(self, out_number, id, site_from, new_time):
        comment_page = 0
        cookie_dict = cookie_to_dict(
            'JSESSIONID=F6406AC900FCDF0F957FB9D6C4F9FDCB.s1; Path=/')
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
                continue
                # cookies = get_jd_cookie()
                # return {'success': False, 'message': "反爬限制", 'out_number': out_number, 'page': comment_page}
            if 'comments' not in result:
                continue
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
            if 'comments' in result and result['comments']:
                for i in result['comments']:
                    comment = {}
                    positive_review = result['productCommentSummary']['goodCount']
                    comment_count = result['productCommentSummary']['commentCount']
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
                    comment['site_from'] = 11
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
                json_data = {
                    'good': {'impression': impression, 'positive_review': positive_review,
                             'comment_count': comment_count, 'id': id, 'site_from': site_from},
                    'data': data,
                }
                # data = json.dumps(data, ensure_ascii=False)
                res = self.comment_save(out_number, json_data, new_time)
                if not res['success']:
                    return res
                if res['message'] == '重复爬取':
                    return {'success': True, 'message': "重复爬取", 'out_number': out_number, 'id': id}
                print("保存成功京东", comment_page, out_number, id)
            pages = result['maxPage']
            if comment_page >= pages or not result['comments']:
                # self.comment_end(out_number, headers['Referer'])
                return {'success': True, 'message': "爬取完成", 'out_number': out_number, 'id': id}
            num = random.randint(self.random_sleep_start, self.random_sleep_end)
            if self.sleep:
                time.sleep(num)
            comment_page += 1

    def data_pdd_handle(self, out_number, id, site_from, new_time):
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
                json_data = {
                    'good': {'impression': '', 'id': id, 'site_from': site_from},
                    'data': data,
                }
                # data = json.dumps(data, ensure_ascii=False)
                res = self.comment_save(out_number, json_data, new_time)
                if not res['success']:
                    return res
                # if res['message'] == '重复爬取':
                #     return {'success': True, 'message': "重复爬取", 'out_number': out_number, 'id': id}
                print("保存成功拼多多", comment_page, out_number, id)
            if not result['data']:
                self.comment_end(out_number, goods_url)
                return {'success': True, 'message': "爬取成功", 'out_number': out_number, 'id': id}
            num = random.randint(self.random_sleep_start, self.random_sleep_end)
            time.sleep(random.randint(5, 8))
            # if self.sleep:
            #     time.sleep(num)
            comment_page += 1

    def data_tmall_handle(self, out_number, id, site_from, new_time):
        comment_page = 1
        while True:
            res = self.get_taobao_impression(out_number, 9)
            if res['success']:
                impression = res['impression']
                break
            time.sleep(5)
        # cookie_list = [
        #     {
        #         't': '7eb89f5c2e118140ef49e1f31237a35e',
        #         '_tb_token_': 'f3e5557aebd57',
        #         'cookie2': '1c695a1217e5b117d4e5225a55e7d40b',
        #         'unb': '2210910815481',
        #         'cookie17': 'UUpgRs05urYo2upivg%3D%3D',
        #     },
        # ]
        cookie_dict = cookie_to_dict(
            'xlly_s=1; cna=BlxpGa3pHwcCAXt1qFue0H25; _m_h5_tk=c5b3a9e5fcb8e7af464b740c33717bcf_1625461046485; _m_h5_tk_enc=854c2cf699871ea9dc8475e4625ae688; dnk=%5Cu658C%5Cu7237%5Cu72371058169464; uc1=cookie21=VT5L2FSpccLuJBreK%2BBd&pas=0&existShop=false&cookie15=Vq8l%2BKCLz3%2F65A%3D%3D&cookie16=VT5L2FSpNgq6fDudInPRgavC%2BQ%3D%3D&cookie14=Uoe2yIdH2plXgA%3D%3D; uc3=id2=UU6m3oSoOMkDcQ%3D%3D&nk2=0rawKUoBrqUrgaRu025xgA%3D%3D&lg2=W5iHLLyFOGW7aA%3D%3D&vt3=F8dCuwOxbPtD9a8VPu0%3D; tracknick=%5Cu658C%5Cu7237%5Cu72371058169464; lid=%E6%96%8C%E7%88%B7%E7%88%B71058169464; _l_g_=Ug%3D%3D; uc4=id4=0%40U2xrc8rNMJFuLuqj%2FSUi4wEzg7hq&nk4=0%400AdtZS03tnds0llDWCRcSihqN1rrIyZSjaqW; unb=2671514723; lgc=%5Cu658C%5Cu7237%5Cu72371058169464; cookie1=BxNSonczp%2BfH4JvkmZGiHVjnsgV7tsFybnrAAaVXt9g%3D; login=true; cookie17=UU6m3oSoOMkDcQ%3D%3D; cookie2=18a7785e1f11a1d863fcadff0362df3e; _nk_=%5Cu658C%5Cu7237%5Cu72371058169464; sgcookie=E1005zv%2Bhz6f5Q0EO2HvAzL3BmLQK8mHDiohVNhyQWporZbAdVivA6gatxv2CBF8mUelPxLo0%2FHtlfIWQt4HF3yB1g%3D%3D; sg=437; t=b471be1b6451e3223c85cf947cb281f6; csg=a23665e3; _tb_token_=3b1f30eaaee70; enc=GW3FaK%2BshiuOkvzRvsW4FqeMe6%2FMvQeuzmtgAyuMTGwNpM93PLvN7bvDd1KcdqQ88O5IlPR6AHOQnMJ7tgQBvw%3D%3D; x5sec=7b22617365727665723b32223a2239393063356638396434666539663662353835323961336132326661613663644349376569596347454f57577664376c2b5a32456d414561444449324e7a45314d5451334d6a4d374d5443756f66474e41673d3d227d; tfstk=c5DfBxAnSZbXPhAN3mtP_PyMtC2Pa0A72IarcXxLApYX_3nbysD1Ly68Ffb5eWE5.; l=eBP6SJ7Vj5lXnq8jBO5wlurza77OmIdfhsPzaNbMiInca1o5ievT1NCB06sBrdtjgt5fVetrFQx-eRUH8f4LRx_ceTwhKXIpBB96Se1..; isg=BKurbzjUTxBGJJNEY1Gj1MWGOs-VwL9CUQZQ9R0pCOpevM0epZHPkqRaFvzSnBc6')
        # cookie_dict = cookie_to_dict('sgcookie=E100nDB%2Fvt%2BlPNVUuHK1rQ5zDPLp%2F1yczzPThqqyjbUWyaB4pjon%2FguTCLdPEjihLGujJfctGXol%2FQ4fdXYRz66qmA%3D%3D; uc1=cookie14=Uoe2yIUfiLbRNA%3D%3D; t=b53111f044cc56cea4bdbd22205e0fe4; uc3=vt3=F8dCuwzn8IuXBz7Zqm0%3D&lg2=URm48syIIVrSKA%3D%3D&nk2=F5RHoWPz3gbNYt4%3D&id2=UUpgRs05urYo2upivg%3D%3D; tracknick=tb202938556; lid=tb202938556; uc4=id4=0%40U2gqyZ2h8V63RJQ0G%2BLPCwib%2Fwu8wfhL&nk4=0%40FY4Ms466dA%2FiBqQDIbngQmsGoTlKvQ%3D%3D; lgc=tb202938556; enc=V7FQMwMAHQy%2BAJxRmZYGoq5cI%2B1fCa7zdA%2FyPaANcQrnv45NgDS3JUECSPxfFuAG2E0SFNWvgg0qm0Qqi%2FmVAtQuTWf6jNAbTtED%2BAz9bfk%3D; _tb_token_=e7131e301193b; cookie2=12f5ca4f815095bfb9bd66c9c635d55b; cna=c2lgGTuTPWYCAXt1qJPODrdS; xlly_s=1; x5sec=7b22617365727665723b32223a223434626438313038326635323763316339356338393961653365393263663037434957556c596347454f5467345033463371486e65526f504d6a49784d446b784d4467784e5451344d5473784d4b366838593043227d; l=eBPOjgiljWcuu65WBO5Zhurza779eQAfCsPzaNbMiInca66ViFk3rNCBVMXWrdtjgtffdetrFQx-eR3M71adgZqhuJ1REpZZQxJM-; tfstk=crndBRtg7CAHpjet32LMPbO3lN4RaiILw9NV2pykPlQRvesRVs4ommHLIewA9lpO.; isg=BBsbP_D9_0dTLAOPhv3bgY8yqn-F8C_yQdYgpQ1awpoc7D7OlcN7QlYqhkziTIfq')
        x5sec = ''
        try:
            with open('design/utils/x5sec.txt', 'r') as f:
                x5sec = f.read().strip()
        except:
            pass
        while True:
            if x5sec:
                cookie_dict['x5sec'] = x5sec
            cookie = dict_to_cookie(cookie_dict)
            proxies = random.choice(self.proxies_list)
            ua = UserAgent().random
            headers = {
                'Referer': 'https://detail.tmall.com/item.htm?id=%s' % out_number,
                'User-Agent': ua,
                'Cookie': cookie
            }
            url = self.comment_tm_data_url % (out_number, comment_page)

            try:
                comment_res = self.s.get(url, headers=headers, verify=False, proxies=proxies, timeout=self.time_out)
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
                # x5sec = asyncio.get_event_loop().run_until_complete(get_pyppeteer_tmall_x5sec(result['url']))
                # x5sec = get_selenium_tmall_x5sec(result['url'])
                x5sec = get_file_tmall_x5sec(result['url'])
                continue
            for i in result['rateDetail']['rateList']:
                comment = {}
                comment['type'] = 1 if i['anony'] else 0
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
                json_data = {
                    'good': {'impression': impression, 'id': id, 'site_from': site_from},
                    'data': data,
                }
                # data = json.dumps(data, ensure_ascii=False)
                res = self.comment_save(out_number, json_data, new_time)
                if not res['success']:
                    return res
                if res['message'] == '重复爬取':
                    return {'success': True, 'message': "重复爬取", 'out_number': out_number, 'id': id}
                print("保存成功天猫", comment_page, out_number, id)
            if 'paginator' not in result['rateDetail']:
                return {'success': True, 'message': "爬取成功", 'out_number': out_number, 'id': id}
            pages = result['rateDetail']['paginator']['lastPage']
            if comment_page >= pages:
                # self.comment_end(out_number, headers['Referer'])
                return {'success': True, 'message': "爬取成功", 'out_number': out_number, 'id': id}
            num = random.randint(self.random_sleep_start, self.random_sleep_end)
            if self.sleep:
                time.sleep(num)
            comment_page += 1

    def data_taobao_handle(self, out_number, id, site_from, new_time):
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
                json_data = {
                    'good': {'impression': impression, 'id': id, 'site_from': site_from},
                    'data': data,
                }
                # data = json.dumps(data, ensure_ascii=False)
                res = self.comment_save(out_number, json_data, new_time)
                if not res['success']:
                    return res
                if res['message'] == '重复爬取':
                    return {'success': True, 'message': "重复爬取", 'out_number': out_number, 'id': id}
                print("保存成功淘宝", comment_page, out_number, id)
            pages = result['maxPage']
            if comment_page >= pages or not result['maxPage']:
                # self.comment_end(out_number, headers['Referer'])
                return {'success': True, 'message': "爬取成功", 'out_number': out_number, 'id': id}
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
        try:
            impression_data = json.loads(rex.findall(impression_res.content.decode('utf-8'))[0])
        except:
            self.logger.error('json load错误')
            return {'success': False, 'message': "json load错误", 'out_number': out_number}
        impression = ''
        if not "tags" in impression_data:
            self.logger.warning('tags 不存在 反爬')
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
        success = False
        while not success:
            try:
                res = requests.get(opalus_goods_comment_url, params=params, verify=False)
                success = True
            except requests.exceptions.RequestException as e:
                logger.warning("获取待爬取商品信息失败 正在重试")
                logger.warning(str(e))
                logger.warning(str(params))
                time.sleep(10)
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


# 手动滑块获取cookie 保存文件
def get_file_tmall_x5sec(url):
    print(url)
    input("1 成功 0 失败：")
    x5sec = ''
    try:
        with open('design/utils/x5sec.txt', 'r') as f:
            x5sec = f.read().strip()
    except:
        pass
    return x5sec


# pyppeteer 滑块验证获取cookie
async def get_pyppeteer_tmall_x5sec(url):
    if not url.startswith('https'):
        url = 'https:' + url
    connect_params = {
        'browserWSEndpoint': 'ws://127.0.0.1:9222/devtools/browser/f58c5278-023b-4187-b967-83bb90b83ca8',
        'logLevel': 3,
    }
    browser = await connect(connect_params)
    page = await browser.newPage()
    # await page.setExtraHTTPHeaders({'Proxy-Authorization': 'Basic ' + ('{"H56R2946P953B99D"}:{"8ADE908B093EFBB9"}').toString('base64')})
    # await page.setExtraHTTPHeaders({'Proxy-Authorization': 'Basic ' + proxyUser + ':' + proxyPass.toString('base64')})
    await page.setViewport({'width': 1366, 'height': 768})
    await page.setUserAgent(
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36')
    await page.evaluate('''() =>{Object.defineProperties(navigator,{webdriver:{get: () => false}})}''')
    await page.evaluateOnNewDocument(
        '() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }')
    await page.evaluate('''() =>{ window.navigator.chrome = { runtime: {},  }; }''')
    await page.evaluate(
        '''() =>{ Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] }); }''')
    await page.evaluate(
        '''() =>{ Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], }); }''')
    await page.goto(url, {'timeout': 1000 * 50})
    await asyncio.sleep(2)
    # 鼠标移动到滑块，按下，滑动到头（然后延时处理），松开按键
    await page.hover('#nc_1_n1z')  # 不同场景的验证码模块能名字不同。
    await page.mouse.down()
    steps = random.randint(58, 80)
    await page.mouse.move(1053, 0, {'steps': 120})
    await asyncio.sleep(2)
    await page.mouse.up()
    await asyncio.sleep(2)
    # title = await page.title()
    cookie_list = await page.cookies()
    for i in cookie_list:
        if i['name'] == 'x5sec':
            x5sec = i['value']
            break
    else:
        x5sec = ''
    return x5sec


# selenium浏览器重新获取cookie
def get_selenium_tmall_x5sec(url):
    if not url.startswith('https'):
        url = 'https:' + url
    # os.system('chrome.exe https://login.taobao.com --remote-debugging-port=9222 --user - data - dir =“C:\selenum\AutomationProfile')
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    # 初始化chrome对象
    browser = webdriver.Chrome(options=chrome_options)
    js = 'window.open("https://www.taobao.com/");'
    browser.execute_script(js)
    browser.close()
    browser.switch_to_window(browser.window_handles[0])
    while True:
        try:
            browser.get(url)
            break
        except:
            pass
    pyautogui_code(browser)
    flag = input("验证成功:")
    if flag == '1':
        x5sec = browser.get_cookie('x5sec')
        if x5sec:
            return x5sec['value']
        else:
            return ''
    else:
        return ''


def pyautogui_code(brower):
    time.sleep(2)
    button_ele = brower.find_element_by_xpath('//*[@id="nc_1_n1z"]')
    button_x = button_ele.location['x'] + 21
    button_y = button_ele.location['y']
    pyautogui.moveTo(button_x, button_y + 90, 0.5)
    div_ele = brower.find_element_by_xpath('//*[@id="nc_1__scale_text"]').size
    # pyautogui.dragTo(button_ele.location['x'] +10 + div_ele['width'], button_ele.location['y']+90, duration=2)
    pyautogui.mouseDown()
    # tracks = get_track(div_ele['width']-20)
    single = (div_ele['width'] - 42) / 10
    a = [21, 23, 25, 27, 29, 31, 33, 35]
    temp = button_x
    for i in a:
        test = random.choice([89,90,91])
        temp += i
        pyautogui.moveTo(temp, button_y + test, 0.01)
    test = random.choice([89,90,91])
    pyautogui.moveTo(button_x + single * 10 - 5, button_y + test, 0.05)
    test = random.choice([89,90,91])
    pyautogui.moveTo(button_x + single * 10 - 4, button_y + test, 0.1)
    test = random.choice([89, 90, 91])
    pyautogui.moveTo(button_x + single * 10 - 2, button_y + test, 0.15)
    test = random.choice([89, 90, 91])
    pyautogui.moveTo(button_x + single * 10 - 1, button_y + test, 0.2)
    test = random.choice([89, 90, 91])
    pyautogui.moveTo(button_x + single * 10 - 0.5, button_y + test, 0.25)
    test = random.choice([89, 90, 91])
    pyautogui.moveTo(button_x + single*10, button_y + test, 0.3)
    time.sleep(1)
    pyautogui.mouseUp()
    time.sleep(2)


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

