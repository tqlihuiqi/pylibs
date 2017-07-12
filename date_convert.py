# -*- coding:utf-8 -*-

import time


def timestamp_to_datetime(timestamp, formatter="%Y-%m-%d %H:%M:%S"):
    """ timestamp格式化为datetime

    :参数 timestamp: 精确到秒的timestamp时间
    :参数 formatter: 格式化后的时间格式，默认: %Y-%m-%d %H:%M:%S
    :返回: CST时间
    """

    ltime = time.localtime(timestamp)
    timeStr = time.strftime(formatter, ltime)
    return timeStr


def datetime_to_timestamp(datetime, formatter="%Y-%m-%d %H:%M:%S"):
    """ datetime格式化为timestamp

    :参数 datetime: 日期时间
    :参数 formatter: 指定传入日期时间的格式，默认: %Y-%m-%d %H:%M:%S
    :返回: timestamp时间
    """

    fmtTime = time.strptime(datetime, formatter)
    return int(time.mktime(fmtTime))


def utctime_to_datetime(utctime, formatter="%Y-%m-%dT%H:%MZ"):
    """ UTC时间格式化当前的CST时间

    :参数 utctime: 传入的UTC时间
    :参数 formatter: 指定传入UTC时间的格式，默认: %Y-%m-%dT%H:%MZ
    :返回: CST时间
    """

    timestamp = int(time.mktime(time.strptime(utctime, formatter))) + 8 * 3600
    return timestamp_to_datetime(timestamp)


if __name__ == "__main__":
    print(timestamp_to_datetime(1499830203))
    print(datetime_to_timestamp("2017-01-01 01:01:01"))
    print(utctime_to_datetime("2017-01-21T01:12:35Z", "%Y-%m-%dT%H:%M:%SZ"))


