# -*- coding:utf-8 -*-

import hashlib
import json
import os
import requests

try:
    from urllib.parse import urlencode
except:
    from urllib import urlencode


class NexusClient(object):
    
    def __init__(self, host, port):
        """ 初始化Nexus客户端设置

        :参数 host: Nexus服务器地址
        :参数 port: Nexus服务器端口
        """

        baseUrl = "http://%s:%s" % (host, port)
        self.versionUrl = baseUrl + "/nexus/service/local/lucene/search?g=%s&a=%s&e=%s"
        self.packageUrl = baseUrl + "/nexus/service/local/artifact/maven/resolve?r=%s&g=%s&a=%s&v=%s&e=%s"
        self.downloadUrl = baseUrl + "/nexus/service/local/repositories/%s/content"
        self.headers = {"accept": "application/json,application/vnd.siesta-error-v1+json,application/vnd.siesta-validation-errors-v1+json"}


    def request(self, url, params={}):
        """ 调用Nexus API接口
        
        :参数 url: 请求的URL地址
        :参数 params: 请求参数, 默认: 空
        """

        if params:
            url = "%s?%s" % (url, urlencode(params))
        
        resp = requests.get(url=url, headers=dict(self.headers))

        return resp.json()


    def get_app_versions(self, group, artifact, package):
        """ 查询应用程序在Nexus中的版本号

        :参数 group: Nexus group参数
        :参数 artifact: Nexus artifact参数
        :参数 package: Nexus package参数
        :返回: 倒序的verison列表
        """

        resp = self.request(url=self.versionUrl % (group, artifact, package))
        versions = [ x["version"] for x in resp["data"] ]

        return versions


    def get_app_download_url(self, group, artifact, package, version, release):
        """ 查询应用程序URL下载地址

        :参数 group: Nexus group参数
        :参数 artifact: Nexus artifact参数
        :参数 package: Nexus package参数
        :参数 version: 应用程序版本号
        :参数 release: 应用程序的发行类型(releases/snapshots)
        :返回: 应用程序下载地址URL
        """

        resp = self.request(url=self.packageUrl % (release, group, artifact, version, package))

        return self.downloadUrl % release + resp["data"]["repositoryPath"]


    def get_app_info(self, url):
       """ 检测应用程序信息

       :参数 url: 应用程序URL下载地址
       :返回: 应用程序名称, 应用程序大小 应用程序MD5
       """

       resp = self.request(url=url, params={"describe": "info"})

       return url.split("/")[-1], round(resp["data"]["size"]/1024/1024, 1), resp["data"]["md5Hash"]


    def download_app(self, url, local, md5):
        """ 下载应用程序，应用程序存在将检测MD5，MD5值相同将跳过下载
        
        :参数 url: 应用程序URL下载地址
        :参数 local: 本地下载路径
        :参数 md5: Nexus中的应用程序MD5值
        :返回: True/False
        """

        appName = url.split("/")[-1]
        appFile = os.path.join(local, appName)

        if os.path.isfile(appFile):
            with open(appFile,"rb") as open_file: 
                existAppMd5 = hashlib.md5(open_file.read()).hexdigest()
            
            if existAppMd5 == md5:
                return True
        
        r = requests.get(url, timeout=10)
        
        with open(appFile, "wb") as wfd:
            wfd.write(r.content)
            
        with open(appFile, "rb") as rfd:
            downloadMd5 = hashlib.md5(rfd.read()).hexdigest()

        if downloadMd5 == md5:
            return True
        
        return False


if __name__ == "__main__":
    nexus = NexusClient(host="127.0.0.1", port=80)
    versions = nexus.get_app_versions(group="com.kafka.consumer", artifact="test-consumer", package="tar.gz")
    downloadUrl = nexus.get_app_download_url(group="com.kafka.consumer", artifact="test-consumer", package="tar.gz", version="0.1", release="releases")
    appName, appSize, appMD5 = nexus.get_app_info(downloadUrl)
    nexus.download_app(url=downloadUrl, local="./", md5=appMD5)
    
