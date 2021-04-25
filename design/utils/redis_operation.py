# -*- coding: utf-8 -*-
#
# Redis database operation method
import redis


class RedisHandle(object):

    def __init__(self, host, port, password=None):
        self.conn = redis.Redis(host, port, password)

    def insert(self, name, key, value):
        self.conn.hset(name, key, value)

    def query(self, name, key):
        rst = self.conn.hget(name, key).decode()
        return rst

    def verify(self, name, key):
        rst = self.conn.hexists(name, key)
        return rst

    def delete(self, name, key):
        if self.verify(name, key):
            self.conn.hdel(name,key)

if __name__ == '__main__':
    RH = RedisHandle('localhost', '6379')