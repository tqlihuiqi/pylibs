# -*- coding:utf-8 -*-

import random
import string

from Crypto.Cipher import AES


def random_password(length):
    """ 密码生成器，生成带有数字、小写字符和大写字符的指定长度的密码

    :参数 length: 指定生成密码长度
    :返回: 指定长度的随机密码
    """

    word = [ s for s in map(str, range(10)) ] + list(string.ascii_letters)
    random.shuffle(word)
    
    return "".join(word)[0:length]


def encrypt_password(key, password):
    """ 使用加密文本加密密码

    :参数 key: 加密密钥，长度必须为16(AES-128), 24(AES-192), 或32(AES-256)Bytes 
    :参数 password: 原文密码，加密文本text必须为16的倍数，如果text不是16的倍数，将补足为16的倍数
    :返回: 加密后的密码
    """

    cryptor = AES.new(key, AES.MODE_CBC, key)
    length = 16
    count = len(password)
    add = length - (count % length)
    password = password + ('\0' * add)
    return cryptor.encrypt(password)


def decrypt_password(key, encrypedPassword):
    """ 使用加密文本解密密码

    :参数 key: 加密密钥，长度必须为16(AES-128), 24(AES-192), 或32(AES-256)Bytes 
    :参数 encrypedPassword: 原文密码，加密文本text必须为16的倍数，如果text不是16的倍数，将补足为16的倍数
    :返回: 解密后的密码原文
    """

    cryptor = AES.new(key, AES.MODE_CBC, key)
    plain_password = cryptor.decrypt(encrypedPassword)
    return plain_password.decode("utf-8").rstrip('\0')


if __name__ == "__main__":
	passwd_16 = random_password(16)
	print(passwd_16)

	enpwd = encrypt_password(key=passwd_16, password="test")
	print(enpwd)

	depwd = decrypt_password(key=passwd_16, encrypedPassword=enpwd)
	print(depwd)


