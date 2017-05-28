import base64
import hashlib
import binascii
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Cipher import XOR
from Crypto.PublicKey import RSA
from Crypto import Random

class AESCipher(object):
    def __init__(self): 
        self.bs = 16
        self.key = '41fb5b5ae4d57c5ee528adb078ac3b2e'

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(self.bs)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return urllib.quote(binascii.hexlify(iv + cipher.encrypt(raw)), safe='')

    def decrypt(self, enc):
        enc = binascii.unhexlify(enc)
        iv = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return cipher.decrypt(enc[16:]).rstrip(PADDING)

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]

class XORCipher():
    @staticmethod
    def decrypt(text):
        key = XOR.new('01101001')
        return key.decrypt(text)

    @staticmethod
    def encrypt(text):
        key = XOR.new('01101001')
        return key.encrypt(text)
    
class RSA1024Cipher():
    @staticmethod
    def generatekeys():
        random_generator = Random.new().read
        key = RSA.generate(1024, random_generator)
        with open('.publickey', 'wb') as the_file:
            the_file.write(key.publickey().exportKey('DER'))
        with open('.privatekey', 'wb') as the_file:
            the_file.write(key.exportKey('DER'))
        return key

    @staticmethod
    def decrypt(text):
        # TO BE IMPLEMENTED
        return text
    
    @staticmethod
    def encrypt(text):
        # TO BE IMPLEMENTED
        return text
