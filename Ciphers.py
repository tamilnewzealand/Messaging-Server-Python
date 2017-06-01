import base64
import hashlib
import binascii
import urllib
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Cipher import XOR
from Crypto.PublicKey import RSA

class AESCipher(object):
    @staticmethod
    def generateKeys():
        return binascii.hexlify(Random.new().read(16))

    @staticmethod
    def encrypt(raw, aeskey):
        raw = AESCipher._pad(raw)
        iv = Random.new().read(16)
        cipher = AES.new(aeskey, AES.MODE_CBC, iv)
        return urllib.quote(binascii.hexlify(iv + cipher.encrypt(raw)), safe='')

    @staticmethod
    def decrypt(enc, aeskey):
        enc = binascii.unhexlify(enc)
        iv = enc[:16]
        cipher = AES.new(aeskey, AES.MODE_CBC, iv)
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
            if thing == 'encryption' or thing == 'destination' or thing == 'sender':
                pass
            else:
                data[thing] = binascii.hexlify(pubkey.encrypt(data[thing], 32)[0])
        data['encryption'] = 3
        return data
    
    @staticmethod
    def encryptValue(value, key):
        pubkey = RSA.importKey(binascii.unhexlify(key))
        return binascii.hexlify(pubkey.encrypt(value, 32)[0])
    
    @staticmethod
    def decrypt(data, key):
        for thing in data:
            if thing == 'encryption' or thing == 'destination' or thing == 'sender':
                pass
            else:
                data[thing] = key.decrypt(binascii.unhexlify(data[thing]))
        return data
    
    @staticmethod
    def decryptValue(value, key):
        return key.decrypt(binascii.unhexlify(value))