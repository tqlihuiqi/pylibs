# -*-coding:utf-8 -*-

import os
import re
import requests
import sys
import time
import uuid

from threading import activeCount, Thread
from Queue import Queue


class Download(object):

    def __init__(self, url, readMB=1, poolSize=5):
        """ 初始化批量下载参数 

        :参数 url: 下载资源地址
        :参数 readMB: 分片下载时每个线程读取的数据大小，默认: 1MB
        :参数 poolSize: 设置分片的线程池大小，防止同时启动过多的分片读取数据损耗系统资源，默认最多可同时运行5个线程
        """

        self.url = url
        self.readBytes = readMB * 1024 * 1024
        
        resp = requests.head(url)
        self.totalBytes = int(resp.headers["Content-Length"])

        try:
            self.filename = eval( re.findall("filename=(\S+)", resp.headers["Content-Disposition"])[0] )
        except:
            self.filename = os.path.basename(url)

        # 检测文件是否存在
        if os.path.isfile(self.filename):
            print("文件已存在: %s" % self.filename)
            sys.exit()

        self.tempdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), str(uuid.uuid4()))
        self.threadPool = Queue(poolSize)

        [ self.threadPool.put(Thread) for _ in range(poolSize) ]


    def delete_temp_dir(self):
        """ 删除分片存储数据的临时目录与目录中的所有数据 """

        files = os.listdir(self.tempdir)

        for file in files:
            path = os.path.join(self.tempdir, file)

            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                delete_user_dir(path)

        os.rmdir(self.tempdir)


    def write_to_file(self, filename, headers=None, useThread=True):
        """ 下载url数据并保存到指定文件中 

        :参数 filename: 将下载的数据保存到该文件中
        :参数 headers: 发送HTTP请求是附加的header，默认为None(使用默认的header)
        :参数 useThread: 是否使用线程进行下载，默认为True(开启使用线程下载)
        """

        resp = requests.get(self.url, headers=headers)

        with open(filename, "ab") as fd:
            fd.write(resp.content)

        if useThread:
            self.threadPool.put(Thread)


    def get(self):
        """ 下载资源 """

        if self.readBytes < self.totalBytes:
            shards = range(self.totalBytes)

            os.mkdir(self.tempdir)

            for i in range(0, self.totalBytes, self.readBytes):
                point = shards[i: i + self.readBytes]
                headers = { "Range": "bytes=%s-%s" % (point[0], point[-1]) }
                filename = os.path.join(self.tempdir, str(point[-1]))

                thread = self.threadPool.get()
                t = thread(target=self.write_to_file, args=[filename, headers])
                t.start()

            while activeCount() > 1:
                time.sleep(1)

            results = sorted(map(int, os.listdir(self.tempdir)))

            with open(self.filename, "ab") as wfd:
                for result in results:
                    f = os.path.join(self.tempdir, str(result))

                    with open(f, "rb") as rfd:
                        content = True

                        while content:
                            content = rfd.read(1024)
                            wfd.write(content)

            self.delete_temp_dir()

        else:
            self.write_to_file(filename=self.filename, useThread=False)


if __name__ == "__main__":
   d = Download(url="https://www.baidu.com/img/baidu_jgylogo3.gif", readMB=1, poolSize=5)
   d.get()