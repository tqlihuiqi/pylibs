#!/usr/bin/env python
# -*- coding:utf-8 -*-

import getopt
import os
import sys

from ftplib import FTP


class FtpClient(object):

    def __init__(self, server, username, password, port=21):
        """ 初始化FTP客户端配置

        :参数 server: FTP服务器地址
        :参数 username: FTP服务器登陆用户名
        :参数 password: FTP服务器登陆密码
        :参数 port: FTP服务器端口, 默认: 21
        """

        self.ftp = FTP()
        self.ftp.connect(server, port)
        self.ftp.login(username, password)


    def __enter__(self):
        return self


    def check_dir(self, target):
        """ 切换FTP指定目录判断目录是否存在
 
        :参数 target: 指定FTP目录
        :返回: True/False
        """
 
        try:
            curr = self.ftp.pwd()
            self.ftp.cwd(target)
            self.ftp.cwd(curr)
            return True
        except:
            return False


    def ftp_list(self, target=None):
        """ 列出指定FTP目录资源

        :参数 target: 指定FTP目录, 默认: None (搜索根目录)
        :显示: 目录中的资源
        """

        self.ftp.dir(target)


    def ftp_get(self, target, local=None):
        """ 递归下载FTP指定目录中的所有资源

        :参数 target: FTP中的资源
        :参数 local: 下载到本地路径, 默认: None (当前目录)
        :返回: True/False
        """

        target = target.strip("/")
        local = local or os.path.abspath(os.path.curdir)

        if not os.path.isdir(local):
            return False

        if self.check_dir(target + "/"):
            local = os.path.join(local, os.path.basename(target))

            if not os.path.isdir(local):
                os.makedirs(local)

            self.ftp.cwd(target)

            for res in self.ftp.nlst():
                self.ftp_get(target=res, local=local)

            self.ftp.cwd("..")

        elif self.ftp.nlst(target):
            with open(os.path.join(local, os.path.basename(target)), "wb") as fd:
                self.ftp.retrbinary("RETR %s" % target, fd.write, 4096)
        
        else:
            return False
                
        return True


    def ftp_put(self, local, target=None):
        """ 递归上传本地指定资源到FTP中

        :参数 local: 本地资源
        :参数 target: 上传的FTP位置, 默认: None (FTP根目录)
        :返回: True/False
        """

        target = target or "/"

        if not os.path.exists(local):
            return False

        if not self.check_dir(target):
            self.ftp.mkd(target)

        if os.path.isdir(local):
            basedir = os.path.dirname(local)
            target = os.path.join(target, os.path.basename(local))

            for res in os.listdir(local):
                local = os.path.join(os.path.join(basedir, os.path.basename(target)), res)
                self.ftp_put(local=local, target=target)

        else:
            res = os.path.basename(local)

            with open(local, "rb") as fd:
                self.ftp.cwd(target)
                self.ftp.storbinary("STOR %s" % res, fd, 4096)
                
        return True


    def ftp_delete(self, target):
        """ 递归删除FTP指定资源

        :参数 target: 删除的FTP资源位置
        :返回: True/False
        """

        if not self.ftp.nlst(target):
            return False

        def _delete(target):
            if self.check_dir(target):
                resources = self.ftp.nlst(target)
                
                if not resources:
                    self.ftp.rmd(target)
    
                else:
                    for res in resources:
                        target = os.path.join(target, res)
                        _delete(target=target)
    
                    if self.check_dir(target):
                        self.ftp.rmd(target)
    
            elif self.ftp.nlst(target):
                self.ftp.delete(target)

        _delete(target)
        self.ftp.rmd(target)

        return True


    def __exit__(self, type, value, traceback):
        """ 关闭FTP客户端链接"""

        self.ftp.close()


if __name__ == "__main__":
    message = """
        [ 帮助 ]
        
        --list    [文件/目录]  
        列出FTP中指定 文件/目录属性
    
        --get     <FTP 文件/目录>  [本地目录]  
        下载FTP中的文件或整个目录, 未指定本地目录将下载当前目录
    
        --put     <本地 文件/目录>  [FTP 文件/目录]
        上传本地文件或整个目录到FTP, 未指定FTP目录将上传到FTP的 "/" 目录

        --delete  <FTP 文件/目录>
        删除FTP中的文件或整个目录


        {} -s <服务器地址> -o <服务器端口> -u <用户名> -p <密码>  --list | ....
    """

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:o:u:p:", ["help", "list", "put=", "get=", "delete="])
        server, port, username, password = [None] * 4
        cmd = {"func": None, "target": None, "local": None}
    
        for name, value in opts:
            if name in ("-h", "--help"):
                print(message.format(sys.argv[0]))
                sys.exit(0)
    
            elif name == "-s":
                server = value
    
            elif name == "-o":
                port = value
    
            elif name == "-u":
                username = value
 
            elif name == "-p":
                password = value

            elif name == "--list":
                cmd["func"] = "list"
                cmd["target"] = value

            elif name == "--get":
                cmd["func"] = "get"
                cmd["target"] = value
                cmd["local"] = len(args) and args[0] or None

            elif name == "--put":
                cmd["func"] = "put"
                cmd["target"] = len(args) and args[0] or None
                cmd["local"] = value

            elif name == "--delete":
                cmd["func"] = "delete"
                cmd["target"] = value

        if not server or not username or not password:
            raise ValueError 

    except:
        sys.exit(1)

    try:
        with FtpClient(server=server, port=port, username=username, password=password) as client:
            if cmd["func"] == "list":
                client.ftp_list(target=cmd["target"])
    
            elif cmd["func"] == "get":
                if client.ftp_get(target=cmd["target"], local=cmd["local"]):
                    print("下载成功")
                else:
                    print("下载失败")
    
            elif cmd["func"] == "put":
                if client.ftp_put(local=cmd["local"], target=cmd["target"]):
                    print("上传成功")
                else:
                    print("上传失败")
    
            elif cmd["func"] == "delete":
                if client.ftp_delete(target=cmd["target"]):
                    print("删除成功")
                else:
                    print("删除失败")
    
    except Exception as e:
        print(e)
        sys.exit(2)

