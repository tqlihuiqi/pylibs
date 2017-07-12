# -*- coding:utf-8 -*-

import codecs
import datetime
import logging
import os
import re


class MultiProcLogHandler(logging.FileHandler):

    def __init__(self, logfile, when="D", retain=1):
        """ 初始化多进程日志切换参数设置

        :参数 logfile: 指定的日志文件
        :参数 when: 日志切换周期 [S, M, H, D], 默认: D
        :参数 retain: 保留日志数量, 默认: 1
        """

        patterns = {
            "S": {"suffix": "%Y-%m-%d_%H-%M-%S", "match": r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}$"},
            "M": {"suffix": "%Y-%m-%d_%H-%M", "match": r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}$"},
            "H": {"suffix": "%Y-%m-%d_%H", "match": r"^\d{4}-\d{2}-\d{2}_\d{2}$"},
            "D": {"suffix": "%Y-%m-%d", "match": r"^\d{4}-\d{2}-\d{2}$"},
        }

        self.logFile = logfile
        self.roll = patterns[when.upper()]
        self.logFileFormat = os.path.join("%s.%s" % (logfile, self.roll["suffix"]))
        self.logFilePath = datetime.datetime.now().strftime(self.logFileFormat)
        self.retain = retain

        super(MultiProcLogHandler, self).__init__(self.logFilePath, "a")


    def check_switch(self):
        """ 检测当前写入日志是否满足切换条件

        :返回: True/False
        """

        currentLogFilePath = datetime.datetime.now().strftime(self.logFileFormat)

        if currentLogFilePath == self.logFilePath:
            return False

        self.logFilePath = currentLogFilePath
        
        return True


    def switch_log(self):
        """ 切换日志文件并删除不满足保留条件的日志 """

        self.baseFilename = os.path.abspath(self.logFilePath)
        
        if self.stream is not None:
            self.stream.flush()
            self.stream.close()

        if not self.delay:
            self.stream = self._open()


    def get_logfile_to_delete(self):
        """ 列出不满足保留条件的日志
        
        :返回: 待删除的日志文件列表
        """

        dirName, _ = os.path.split(self.baseFilename)
        prefix = os.path.basename(self.logFile) + "."
        plen = len(prefix)
        result = []

        for logFile in os.listdir(dirName):
            if logFile[:plen] == prefix:
                suffix = logFile[plen:]
                
                if re.compile(self.roll["match"]).match(suffix):
                    result.append(os.path.join(dirName, logFile))
        
        result.sort()

        if len(result) < self.retain:
            result = []
        else:
            result = result[:len(result) - self.retain]

        return result  


    def emit(self, record):
        """ 记录日志 切换日志 删除日志 
        
        :参数 record: 日志条目
        """
 
        try:
            if self.check_switch():
                self.switch_log()

            if self.retain > 0:
                for s in self.get_logfile_to_delete():
                    os.remove(s)

            logging.FileHandler.emit(self, record)
            
        except (KeyboardInterrupt, SystemExit):
            raise
        
        except:
            self.handleError(record)


if __name__ == "__main__":
    logHandler = MultiProcLogHandler(logfile="./test.log", when="D", retain=2)
    logHandler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    
    log = logging.getLogger("test")
    log.setLevel(logging.INFO)
    log.addHandler(logHandler)

    log.info("test info")
    log.error("test error")
    log.warning("test warn")
