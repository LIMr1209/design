# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
#
from pymongo import MongoClient
from design.settings import MONGODB_HOST, MONGODB_PORT, MONGODB_DBNAME, SHEETE_NAME
import random
import requests
import json
import base64
from io import BytesIO
import time
import os


def baidu_image(dict_item, headers, path):
    img_url = dict_item['img_url']
    try:
        img_response = requests.get(img_url, headers=headers, timeout=5)
        a = int(time.time())
        b = random.randint(10, 100)
        num = str(a) + str(b)
        try:
            with open(path + '\\' + num + '.jpg', 'wb') as file:
                file.write(img_response.content)
            print('保存图片成功', img_url)
        except:
            print('保存图片失败', img_url)
    except:
        print('访问图片失败', img_url)


def other_image(dict_item, headers, path):
    img_urls = dict_item['img_urls']
    for url in img_urls:
        try:
            img_response = requests.get(url, headers=headers, timeout=5)
            # num = str(a) + str(b)
            img_file = url.split('/')[-1]
            if dict_item['channel'] == 'suning' or dict_item['channel'] == "amazon":
                img_file = img_file.split('.')[0]+'.jpg'
            if dict_item["channel"] == "samsonite" or dict_item['channel'] == "tumi" or dict_item['channel'] == "americantourister":
                a = int(time.time())
                b = random.randint(10, 100)
                img_file = str(a) + str(b)+'.jpg'
            try:
                if img_response.status_code == 200:
                    with open(path + '\\' + img_file, 'wb') as file:
                        file.write(img_response.content)
                    print('保存图片成功', url)
                else:
                    print('访问图片失败', url)
            except:
                print('保存图片失败', url)
        except:
            print('访问图片失败', url)


class ImageSavePipeline(object):
    def __init__(self):
        pass

    def open_spider(self, spider):
        pass

    def process_item(self, item, spider):
        dict_item = dict(item)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0'}
        label_name = dict_item['tag']
        path = 'C:\\Users\\aaa10\\Desktop\\image\\' + label_name+'_'+dict_item['channel']
        if not os.path.exists(path):
            os.makedirs(path)
        if dict_item['channel'] == 'baidu':
            baidu_image(dict_item, headers, path)
        else:
            other_image(dict_item, headers, path)
        return item

    def close_spider(self, spider):
        pass


class ImagePipeline(object):
    def __init__(self):
        self.url = 'https://www.taihuoniao.com/api/product/submit'
        # self.url = 'http://dev.taihuoniao.com/api/product/submit'
        # self.url = 'http://127.0.0.1:8004/api/product/submit'

    def open_spider(self, spider):
        pass

    def process_item(self, item, spider):
        dict_item = dict(item)
        response = requests.post(self.url, data=dict_item, verify=False)
        res = json.loads(response.content.decode('utf-8'))
        if res['code'] == 3011:
            b = 1
        print(res)

    def close_spider(self, spider):
        pass


class EasyDlPipeline(object):
    def __init__(self):
        pass

    def open_spider(self, spider):
        mogo_cli = MongoClient(MONGODB_HOST, MONGODB_PORT)
        db = mogo_cli[MONGODB_DBNAME]
        self.collection = db[SHEETE_NAME]

    def process_item(self, item, spider):
        dict_item = dict(item)
        result = self.collection.find_one(dict_item)
        if result:
            return item
        else:
            label_name = dict_item['tag']
            if not os.path.exists('./image/' + label_name):
                os.makedirs('./image/' + label_name)
            # file_name = []
            for i, img_url in enumerate(item['img_urls']):
                a = int(time.time())
                b = random.randint(10, 100)
                num = str(a) + str(b)
                img_response = requests.get(img_url)
                with open('./image/' + label_name + '/' + num + '.jpg', 'wb') as file:
                    file.write(img_response.content)
                # img_data = base64.b64encode(BytesIO(img_response.content).read()).decode('utf-8')
                # result = ds.tag_add(23657, entity_content=img_data, entity_name=num + '.jpg',
                #                     labels=[{'label_name': label_name}])
                # if result:
                #     print(result, '失败数据', img_url)
                #     dict_item['img_urls'].pop(i)
                # else:
                #     with open('./image/' + label_name + '/' + num + '.jpg', 'wb') as file:
                #         file.write(img_response.content)
                #     file_name.append(num + '.jpg')
            # dict_item['file_name'] = file_name
            # self.collection.insert_one(dict_item)
            return item

    def close_spider(self, spider):
        pass


# 数据集管理
class DSManger:
    headers = {'Content-Type': 'application/json'}
    host = {
        'ds_add': 'https://aip.baidubce.com/rpc/2.0/easydl/dataset/create',
        'ds_list': 'https://aip.baidubce.com/rpc/2.0/easydl/dataset/list',
        'tag_list': 'https://aip.baidubce.com/rpc/2.0/easydl/label/list',
        'tag_add': 'https://aip.baidubce.com/rpc/2.0/easydl/dataset/addentity',
        'ds_delete': 'https://aip.baidubce.com/rpc/2.0/easydl/dataset/delete',
        'tag_delete': 'https://aip.baidubce.com/rpc/2.0/easydl/label/delete'
    }
    type = 'IMAGE_CLASSIFICATION'

    # 获取access_token
    # client_id 为官网获取的AK， client_secret 为官网获取的SK
    def get_access_token(self, client_id, client_secret):
        acc_host = 'https://aip.baidubce.com/oauth/2.0/token'
        params = {'grant_type': 'client_credentials', 'client_id': client_id, 'client_secret': client_secret}
        response = requests.get(acc_host, headers=self.headers, params=params)
        content = json.loads(response.text)
        if 'error' in content:
            print('获取access_token失败')
            return
        access_token = content['access_token']
        self.params = {'access_token': access_token}

    # 创建数据集
    def ds_add(self, dataset_name):
        data = json.dumps({'type': self.type, 'dataset_name': dataset_name}, ensure_ascii=True)
        response = requests.post(self.host['ds_add'], data=data, headers=self.headers, params=self.params)
        result = json.loads(response.text)
        if 'error_code' in result:
            print('创建数据集失败')
            print(result)
            return
        return result['dataset_id']  # 返回数据集id

    # 数据集列表
    def ds_list(self):
        data = json.dumps({'type': 'IMAGE_CLASSIFICATION'})
        response = requests.post(self.host['ds_list'], data=data, params=self.params, headers=self.headers)
        result = json.loads(response.content.decode('utf-8'))
        if 'error_code' in result:
            print('获取数据集列表失败')
            return
        return result['results']  # 返回数据集列表

    # 删除数据集
    def ds_delete(self, dataset_id):
        data = json.dumps({'type': self.type, 'dataset_id': dataset_id})
        response = requests.post(self.host['ds_delete'], data=data, params=self.params, headers=self.headers)
        result = json.loads(response.text)
        if 'error_code' in result:
            print('删除数据集失败')
            return

    # 添加分类数据
    # appendLabel 确定添加标签/分类的行为：追加(true)、替换(false)。默认为追加(true)。
    # entity_content 图片base64编码，entity_name 文件名
    # labels 标签/分类数据  object  {label_name 标签/分类名称 }
    def tag_add(self, dataset_id, entity_content, entity_name, labels, appendLabel=True):
        data = json.dumps({
            'type': self.type,
            'dataset_id': dataset_id,
            'appendLabel': appendLabel,
            'entity_content': entity_content,
            'entity_name': entity_name,
            'labels': labels,
        })
        response = requests.post(self.host['tag_add'], data=data, params=self.params, headers=self.headers)
        result = json.loads(response.text)
        if 'error_code' in result:
            print('添加分类数据失败')
            return result
        print(result)

    # 分类列表
    def tag_list(self, dataset_id):
        data = json.dumps({'type': self.type, 'dataset_id': dataset_id})
        response = requests.post(self.host['tag_list'], data=data, params=self.params, headers=self.headers)
        result = json.loads(response.text)
        if 'error_code' in result:
            print('查看分类列表失败')
            return
        return result['results']

    # 删除分类
    def tag_delete(self, dataset_id, label_name):
        data = json.dumps({'type': self.type, 'dataset_id': dataset_id, 'label_name': label_name})
        response = requests.post(self.host['tag_delete'], data=data, params=self.params, headers=self.headers)
        result = json.loads(response.text)
        if 'error_code' in result:
            print('删除分类失败')
            return


# ds = DSManger()
# ds.get_access_token('2GzP6I50zxHOqQ66zyKdRMT3', '5VL8eL2IFKH61CxjSv55CvCWGdcFogr0')
