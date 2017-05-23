import base64
import hashlib
import ascii
from Crypto import Random
from Crypto.Cipher import AES

class AESCipher(object):
    def __init__(self, key): 
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