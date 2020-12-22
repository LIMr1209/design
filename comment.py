import json
import random
import re
import time
import requests
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter


class CommentSpider:
    def __init__(self, name):
        self.name = name
        s = requests.Session()
        s.mount('http://', HTTPAdapter(max_retries=5))  # 重试次数
        s.mount('https://', HTTPAdapter(max_retries=5))
        self.s = s
        # 代理列表
        self.proxies_list = [{'http': ''}]
        # pdd 用户认证列表
        self.pdd_accessToken_list = ['OSAR37W2Z26BM7JKEJAZMFDXNFNO3IKEMINREDOO3SEA7DITK7VQ1128855']
        self.time_out = 10
        self.random_sleep_start = 5
        self.random_sleep_end = 10
        if name == 'jd':
            self.comment_data_url = 'https://club.jd.com/comment/skuProductPageComments.action?callback=fetchJSON_comment98&productId=%s&score=0&sortType=5&page=%s&pageSize=10&isShadowSku=0&fold=1'
            # 有的商品 当前sku 无评论 切换url
            self.switch = False
        elif name == 'pdd':
            self.comment_data_url = 'http://yangkeduo.com/proxy/api/reviews/%s/list?pdduid=9575597704&page=%s&size=20&enable_video=1&enable_group_review=1&label_id=0'
        elif name == 'taobao':
            self.comment_data_url = 'https://rate.taobao.com/feedRateList.htm?auctionNumId=%s&currentPageNum=%s&pageSize=20&orderType=sort_weight&attribute=&sku=&hasSku=false&folded=0&callback=jsonp_tbcrate_reviews_list'
        elif name == 'tmall':
            self.comment_data_url = 'https://rate.tmall.com/list_detail_rate.htm?itemId=%s&spuId=972811287&sellerId=2901218787&order=3&currentPage=%s&append=0&content=1&tagId=&posi=&picture=&groupId=&needFold=0&_ksTS=1606704651028_691&callback=jsonp692'
        self.comment_save_url = 'https://opalus.d3ingo.com/api/comment/save'
        # self.comment_save_url = 'http://opalus-dev.taihuoniao.com/api/comment/save'
        # self.comment_save_url = 'http://127.0.0.1:8002/api/comment/save'

    # 保存评论
    def comment_save(self, out_number, data):
        try:
            res = self.s.post(self.comment_save_url, data=data)
        except requests.exceptions.RequestException as e:
            return {'success': False, 'message': "保存失败", 'out_number': out_number}
        if res.status_code != 200 or json.loads(res.content)['code']:
            message = json.loads(res.content)['message']
            return {'success': False, 'message': message, 'out_number': out_number}

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

    def data_handle(self, out_number):
        if self.name == 'jd':
            res = self.data_jd_handle(out_number)
        elif self.name == 'pdd':
            res = self.data_pdd_handle(out_number)
        elif self.name == 'tmall':
            res = self.data_tmall_handle(out_number)
        elif self.name == 'taobao':
            res = self.data_taobao_handle(out_number)
        return res

    def data_jd_handle(self, out_number):
        comment_page = 0
        while True:
            comment_res = ''
            proxies = random.choice(self.proxies_list)
            ua = UserAgent().random
            headers = {
                'Referer': 'https://item.jd.com/%s.html' % out_number,
                # 'User-Agent': ua,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
                'Cookie': '__jdv=76161171|direct|-|none|-|1608255795687; areaId=1; PCSYCityID=CN_110000_110100_110105; shshshfpa=1ea06a98-4acf-4194-8612-1f53aa095576-1608255797; shshshfpb=ptjkzrtRv%2FGXDRxvbTmMhXQ%3D%3D; ipLoc-djd=1-72-55653-0; jwotest_product=99; __jdu=16082557956851132232680; __jda=122270672.16082557956851132232680.1608255796.1608528276.1608546540.6; __jdc=122270672; shshshfp=e617994739299fc7d65b757f312bf7d1; 3AB9D23F7A4B3C9B=E7MDYEC5EOP32SWZP4FX4FOIZPNTF5NSHBOUS3IOKPFAUDJLD5FWSZSRWQUHEH5UA3DNBXQEWWVPPHK4LXTIDWNONE; shshshsID=fc4275835fb93217e88bce5600d92c29_5_1608547125459; __jdb=122270672.5.16082557956851132232680|6.1608546540; JSESSIONID=02182E6AC1F7B1F35FA6123414378436.s1',
            }
            # if comment_res:
            #     headers['Cookie'] = comment_res.headers.get('set-cookie')[1]
            url = self.comment_data_url % (out_number, comment_page)

            try:
                comment_res = self.s.get(url, headers=headers, proxies=proxies, verify=False, timeout=10)
            except requests.exceptions.RequestException as e:
                return {'success': False, 'message': "反爬限制", 'out_number': out_number}

            # 54 好评 3 2 中评 1 差评
            rex = re.compile('({.*})')
            try:
                result = json.loads(rex.findall(comment_res.text)[0])
            except:
                return {'success': False, 'message': "反爬限制", 'out_number': out_number}
            if comment_page == 0 and not result['comments'] and not self.switch:
                self.comment_data_url = 'https://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98&productId=%s&score=0&sortType=5&page=%s&pageSize=10&isShadowSku=0&fold=1'
                self.switch = True
                continue

            for i in result['comments']:
                comment = {}
                comment['positive_review'] = result['productCommentSummary']['goodCount']
                comment['comment_count'] = result['productCommentSummary']['commentCount']
                impression = ''
                for j in result['hotCommentTagStatistics']:
                    impression += j['name'] + '(' + str(j['count']) + ')  '
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
                self.comment_save(out_number, comment)
            pages = result['maxPage']
            if comment_page >= pages or not result['comments']:
                self.comment_end(out_number, headers)
                return {'success': True, 'message': "爬取完成", 'out_number': out_number}
            num = random.randint(self.random_sleep_start, self.random_sleep_end)
            time.sleep(num)
            comment_page += 1

    def data_pdd_handle(self, out_number):
        comment_page = 1
        while True:
            proxies = random.choice(self.proxies_list)
            ua = UserAgent().random
            headers = {
                'Referer': 'http://yangkeduo.com/goods_comments.html?goods_id=%s' % out_number,
                'User-Agent': ua,
                'AccessToken': random.choice(self.pdd_accessToken_list),
                'VerifyAuthToken': 'yiNF63KwVYtT3frnBC1Rvw9a0471827507f365b',
            }
            url = self.comment_data_url % (out_number, comment_page)

            try:
                comment_res = self.s.get(url, headers=headers, proxies=proxies, verify=False, timeout=10)
            except requests.exceptions.RequestException as e:
                return {'success': False, 'message': "反爬限制", 'out_number': out_number}
            result = json.loads(comment_res.content)
            if 'empty_comment_text' not in result:
                return {'success': False, 'message': "反爬限制", 'out_number': out_number}

            for i in result['data']:
                comment = {}
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
                self.comment_save(out_number, comment)
            if not result['data']:
                self.comment_end(out_number, headers)
                return {'success': True, 'message': "爬取成功", 'out_number': out_number}
            num = random.randint(self.random_sleep_start, self.random_sleep_end)
            time.sleep(num)
            comment_page += 1

    def data_tmall_handle(self, out_number):
        comment_impression = 'https://rate.tmall.com/listTagClouds.htm?itemId=%s&isAll=true&isInner=true'
        proxies = random.choice(self.proxies_list)
        ua = UserAgent().random
        headers = {
            'Referer': 'https://detail.tmall.com/item.htm?&id=564891421863',
            'User-Agent': ua,
            'Cookie': '_bl_uid=vjkhyfh1kL3up48m99pCr7FrpXtk; _m_h5_tk=a4901680887df4de35e80eca7db44b84_1606823592784; _m_h5_tk_enc=9bc810f0923b6d2ffa1255ef0eb10aee; t=4c621df8e85d4fe9067ccde6f510e986; cookie2=19f934d02e95023c00ef6f6c16247b20; _tb_token_=538f3e759d683; _samesite_flag_=true; xlly_s=1; enc=8VjKAvR5cUAIjOxlCLOZcKJvrc68jolYx%2B%2BXKZSjT9%2FFz8LyOvCmZRJkDd6PtDwSKarI7PYNAY8Xh0A58XSpGw%3D%3D; thw=cn; hng=CN%7Czh-CN%7CCNY%7C156; mt=ci=0_0; tracknick=; uc1=cookie14=Uoe0az6%2FCczAvQ%3D%3D; cna=zasMF12t3zoCATzCuQKpN3kO; v=0; x5sec=7b22726174656d616e616765723b32223a226536393430633233383332336665616466656166333533376635366463646233434c76446d50344645497165377565426c734f453767453d227d; l=eBjqXoucQKR1C6x3BO5aourza779rLAXhsPzaNbMiIncC6pCdopMGYxQKOsKgCtRR8XAMTLB4mWKOPytfF1gJs8X7w3xU-CtloD2B; tfstk=cyklBRcOcbP7_BVm1LwSjSvcCLyhC8Tzzvk-3xwwcEPL8GLYV75cWs5ZriK0u4DdO; isg=BC0t6dP2Dkp6levKmUHve7J9PMmnimFctAAvaW84I0aR5kOYN9gnLBbw0LoA5nkU'
        }
        impression_res = requests.get(comment_impression % out_number, stream=True, headers=headers, proxies=proxies,
                                      verify=False, timeout=10)
        rex = re.compile('({.*})')
        impression_data = json.loads(rex.findall(impression_res.content.decode('utf-8'))[0])
        impression = ''
        for i in impression_data['tags']['tagClouds']:
            impression += i['tag'] + '(' + str(i['count']) + ')  '
        comment_page = 1
        while True:
            proxies = random.choice(self.proxies_list)
            ua = UserAgent().random
            headers = {
                'Referer': 'https://detail.tmall.com/item.htm?&id=564891421863',
                'User-Agent': ua,
                'Cookie': '_bl_uid=vjkhyfh1kL3up48m99pCr7FrpXtk; _m_h5_tk=a4901680887df4de35e80eca7db44b84_1606823592784; _m_h5_tk_enc=9bc810f0923b6d2ffa1255ef0eb10aee; t=4c621df8e85d4fe9067ccde6f510e986; cookie2=19f934d02e95023c00ef6f6c16247b20; _tb_token_=538f3e759d683; _samesite_flag_=true; xlly_s=1; enc=8VjKAvR5cUAIjOxlCLOZcKJvrc68jolYx%2B%2BXKZSjT9%2FFz8LyOvCmZRJkDd6PtDwSKarI7PYNAY8Xh0A58XSpGw%3D%3D; thw=cn; hng=CN%7Czh-CN%7CCNY%7C156; mt=ci=0_0; tracknick=; uc1=cookie14=Uoe0az6%2FCczAvQ%3D%3D; cna=zasMF12t3zoCATzCuQKpN3kO; v=0; x5sec=7b22726174656d616e616765723b32223a226536393430633233383332336665616466656166333533376635366463646233434c76446d50344645497165377565426c734f453767453d227d; l=eBjqXoucQKR1C6x3BO5aourza779rLAXhsPzaNbMiIncC6pCdopMGYxQKOsKgCtRR8XAMTLB4mWKOPytfF1gJs8X7w3xU-CtloD2B; tfstk=cyklBRcOcbP7_BVm1LwSjSvcCLyhC8Tzzvk-3xwwcEPL8GLYV75cWs5ZriK0u4DdO; isg=BC0t6dP2Dkp6levKmUHve7J9PMmnimFctAAvaW84I0aR5kOYN9gnLBbw0LoA5nkU'
            }
            url = self.comment_data_url % (out_number, comment_page)

            try:
                comment_res = self.s.get(url, headers=headers, proxies=proxies, verify=False, timeout=10)
            except requests.exceptions.RequestException as e:
                return {'success': False, 'message': "反爬限制", 'out_number': out_number}
            rex = re.compile('({.*})')
            result = json.loads(rex.findall(comment_res.content.decode('utf-8'))[0])
            for i in result['rateDetail']['rateList']:
                comment = {}
                comment['impression'] = impression
                comment['type'] = 1 if i['anony'] else 0
                comment['good_url'] = headers['Referer']
                comment['site_from'] = 9
                if i['rateContent'] == '此用户没有填写评论!':
                    comment['first'] = ''
                else:
                    comment['first'] = i['rateContent']
                comment['add'] = i['appendComment']['content'] if i['appendComment'] else ''
                comment['buyer'] = i['displayUserNick']
                comment['style'] = i['auctionSku']
                comment['date'] = i['rateDate']
                self.comment_save(out_number, comment)
            pages = result['rateDetail']['paginator']['lastPage']
            if comment_page >= pages:
                self.comment_end(out_number, headers)
                return {'success': True, 'message': "爬取成功", 'out_number': out_number}
            num = random.randint(self.random_sleep_start, self.random_sleep_end)
            time.sleep(num)
            comment_page += 1

    def data_taobao_handle(self, out_number):
        comment_impression = 'https://rate.tmall.com/listTagClouds.htm?itemId=%s&isAll=true&isInner=true'
        proxies = random.choice(self.proxies_list)
        ua = UserAgent().random
        headers = {
            'Referer': 'https://item.taobao.com/item.htm?&id=' + out_number,
            'User-Agent': ua,
            'Cookie': '_bl_uid=vjkhyfh1kL3up48m99pCr7FrpXtk; _m_h5_tk=a4901680887df4de35e80eca7db44b84_1606823592784; _m_h5_tk_enc=9bc810f0923b6d2ffa1255ef0eb10aee; t=4c621df8e85d4fe9067ccde6f510e986; cookie2=19f934d02e95023c00ef6f6c16247b20; _tb_token_=538f3e759d683; _samesite_flag_=true; xlly_s=1; enc=8VjKAvR5cUAIjOxlCLOZcKJvrc68jolYx%2B%2BXKZSjT9%2FFz8LyOvCmZRJkDd6PtDwSKarI7PYNAY8Xh0A58XSpGw%3D%3D; thw=cn; hng=CN%7Czh-CN%7CCNY%7C156; mt=ci=0_0; tracknick=; uc1=cookie14=Uoe0az6%2FCczAvQ%3D%3D; cna=zasMF12t3zoCATzCuQKpN3kO; v=0; x5sec=7b22726174656d616e616765723b32223a226536393430633233383332336665616466656166333533376635366463646233434c76446d50344645497165377565426c734f453767453d227d; l=eBjqXoucQKR1C6x3BO5aourza779rLAXhsPzaNbMiIncC6pCdopMGYxQKOsKgCtRR8XAMTLB4mWKOPytfF1gJs8X7w3xU-CtloD2B; tfstk=cyklBRcOcbP7_BVm1LwSjSvcCLyhC8Tzzvk-3xwwcEPL8GLYV75cWs5ZriK0u4DdO; isg=BC0t6dP2Dkp6levKmUHve7J9PMmnimFctAAvaW84I0aR5kOYN9gnLBbw0LoA5nkU'
        }
        impression_res = requests.get(comment_impression % out_number, stream=True, headers=headers, proxies=proxies,
                                      verify=False, timeout=10)
        rex = re.compile('({.*})')
        impression_data = json.loads(rex.findall(impression_res.content.decode('utf-8'))[0])
        impression = ''
        for i in impression_data['tags']['tagClouds']:
            impression += i['tag'] + '(' + str(i['count']) + ')  '
        comment_page = 1
        while True:
            proxies = random.choice(self.proxies_list)
            ua = UserAgent().random
            headers = {
                'Referer': 'https://item.taobao.com/item.htm?id=' + out_number,
                'User-Agent': ua,
                'Cookie': '_bl_uid=vjkhyfh1kL3up48m99pCr7FrpXtk; _m_h5_tk=a4901680887df4de35e80eca7db44b84_1606823592784; _m_h5_tk_enc=9bc810f0923b6d2ffa1255ef0eb10aee; t=4c621df8e85d4fe9067ccde6f510e986; cookie2=19f934d02e95023c00ef6f6c16247b20; _tb_token_=538f3e759d683; _samesite_flag_=true; xlly_s=1; enc=8VjKAvR5cUAIjOxlCLOZcKJvrc68jolYx%2B%2BXKZSjT9%2FFz8LyOvCmZRJkDd6PtDwSKarI7PYNAY8Xh0A58XSpGw%3D%3D; thw=cn; hng=CN%7Czh-CN%7CCNY%7C156; mt=ci=0_0; tracknick=; uc1=cookie14=Uoe0az6%2FCczAvQ%3D%3D; cna=zasMF12t3zoCATzCuQKpN3kO; v=0; x5sec=7b22726174656d616e616765723b32223a226536393430633233383332336665616466656166333533376635366463646233434c76446d50344645497165377565426c734f453767453d227d; l=eBjqXoucQKR1C6x3BO5aourza779rLAXhsPzaNbMiIncC6pCdopMGYxQKOsKgCtRR8XAMTLB4mWKOPytfF1gJs8X7w3xU-CtloD2B; tfstk=cyklBRcOcbP7_BVm1LwSjSvcCLyhC8Tzzvk-3xwwcEPL8GLYV75cWs5ZriK0u4DdO; isg=BC0t6dP2Dkp6levKmUHve7J9PMmnimFctAAvaW84I0aR5kOYN9gnLBbw0LoA5nkU'
            }
            url = self.comment_data_url % (out_number, comment_page)

            try:
                comment_res = self.s.get(url, headers=headers, proxies=proxies, verify=False, timeout=10)
            except requests.exceptions.RequestException as e:
                return {'success': False, 'message': "反爬限制", 'out_number': out_number}
            rex = re.compile('({.*})')
            result = json.loads(rex.findall(comment_res.content.decode('utf-8'))[0])
            for i in result['comments']:
                comment = {}
                if i['rate'] == "1":
                    comment['type'] = 0
                elif i['rate'] == "0":
                    comment['type'] = 2
                elif i['rate'] == "-1":
                    comment['type'] = 1
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
                self.comment_save(out_number, comment)
            pages = result['maxPage']
            if comment_page >= pages or not result['maxPage']:
                self.comment_end(out_number, headers)
                return {'success': True, 'message': "爬取成功", 'out_number': out_number}
            num = random.randint(self.random_sleep_start, self.random_sleep_end)
            time.sleep(num)
            comment_page += 1


import sys


def comment_spider(name, category):
    params = {'category': category}
    if name == 'jd':
        params['site_from'] = 11
    elif name == 'pdd':
        params['site_from'] = 10
    elif name == 'tmall':
        params['site_from'] = 9
    elif name == 'taobao':
        params['site_from'] = 8
    res = requests.get('https://opalus.d3ingo.com/api/good_comment', params=params,verify=False)
    res = json.loads(res.content)
    spider = CommentSpider(name=name)
    for i in res['data']:
        res = spider.data_handle(str(i['number']))
        print(res)
        if not res['success']:
            break

if __name__ == '__main__':
    import urllib3
    urllib3.disable_warnings()
    comment_spider(sys.argv[1], sys.argv[2])
