import base64
import hashlib
import binascii
import urllib
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Cipher import XOR
from Crypto.PublicKey import RSA
from Crypto import Random

class AESCipher(object):
    @staticmethod
    def encrypt(raw):
        raw = AESCipher._pad(raw)
        iv = Random.new().read(16)
        cipher = AES.new('41fb5b5ae4d57c5ee528adb078ac3b2e', AES.MODE_CBC, iv)
        return urllib.quote(binascii.hexlify(iv + cipher.encrypt(raw)), safe='')

    @staticmethod
    def decrypt(enc):
        enc = binascii.unhexlify(enc)
        iv = enc[:16]
        cipher = AES.new('41fb5b5ae4d57c5ee528adb078ac3b2e', AES.MODE_CBC, iv)
        return cipher.decrypt(enc[16:]).rstrip(' ')

    @staticmethod
    def _pad(s):
        return s + (16 - len(s) % 16) * chr(32)

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
        return key
    
    @staticmethod
    def encrypt(data, key):
        pubkey = RSA.importKey(binascii.unhexlify(key))
        for thing in data:
            if data[thing] == data['encryption'] or data[thing] == data['destination']:
                pass
            else:
                if len(unicode(data[thing])) > 128:
                    text = data[thing]
                    n = 128
                    [text[i:i+n] for i in range(0, len(text), n)]
                    for block in text:
                        block = binascii.hexlify(pubkey.encrypt(block, 32))
                    data[thing] = ''.join(text)
                else:
                    data[thing] = binascii.hexlify(pubkey.encrypt(data[thing], 32))
        data['encryption'] = '3'
        return data