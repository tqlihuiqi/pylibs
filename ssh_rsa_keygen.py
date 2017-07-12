# -*- coding:utf-8 -*-

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend


class SSHKeyGen(object):

    @staticmethod
    def gen(bits=1024, password=None):
        """ 生成SSH RSA密钥对
 
        :参数 bits: 密钥加密长度，默认: 1024
        :参数 password: 指定密钥密码，默认: None (不加密)
        :返回: RSA私钥, RSA公钥
        """

        rsaKey = rsa.generate_private_key(
            backend = default_backend(), 
            public_exponent = 65537, 
            key_size = bits
        )

        privateKey = rsaKey.private_bytes(
            encoding = serialization.Encoding.PEM, 
            format = serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm = password and serialization.BestAvailableEncryption(str(password).encode("utf-8")) or serialization.NoEncryption()
        ).decode("utf-8")

        publicKey = rsaKey.public_key().public_bytes(
            encoding = serialization.Encoding.OpenSSH, 
            format = serialization.PublicFormat.OpenSSH
        ).decode("utf-8")

        return privateKey, publicKey


if __name__ == "__main__":
    priviteKey, publicKey = SSHKeyGen.gen()
    priviteKey, publicKey = SSHKeyGen.gen(bits=2048, password="test")

