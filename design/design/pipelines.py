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


class ImagePipeline(object):
    def __init__(self):
        self.url = 'http://opalus.taihuoniao.com/api/produce/submit'
        # self.url = 'http://opalus-dev.taihuoniao.com/api/produce/submit'
        # self.url = 'http://127.0.0.1:8002/api/produce/submit'
        # self.url = 'http://127.0.0.1:8002/api/image/submit'

    def open_spider(self, spider):
        pass

    def process_item(self, item, spider):
        dict_item = dict(item)
        response = requests.post(self.url, data=dict_item)
        print(response.content)

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
            if not os.path.exists('./image/'+label_name):
                os.makedirs('./image/'+label_name)
            for i, img_url in enumerate(item['img_urls']):
                a = int(time.time())
                b = random.randint(10, 100)
                num = str(a) + str(b)
                img_response = requests.get(img_url)
                with open('./image/' + label_name + '/' +num + '.jpg', 'wb') as file:
                    file.write(img_response.content)
                # img_data = base64.b64encode(BytesIO(img_response.content).read()).decode('utf-8')
                # result = ds.tag_add(23051, entity_content=img_data, entity_name=str(num)+'.jpg',
                #                     labels=[{'label_name': label_name}])
                # if result:
                #     print(result, '失败数据', img_url)
                dict_item['file_name'] = num+'.jpg'
                self.collection.insert_one(dict_item)
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


ds = DSManger()
ds.get_access_token('2GzP6I50zxHOqQ66zyKdRMT3', '5VL8eL2IFKH61CxjSv55CvCWGdcFogr0')
