# coding=utf8

import time
import Ciphers
from Crypto.Hash import SHA256
from Crypto.Hash import SHA512
from passlib.hash import bcrypt
from passlib.hash import scrypt
import bleach
import binascii
import db
import urllib2

def unprocess(data, listLoggedInUsers):
    if 'encryption' not in data:
        data['encryption'] = 0
    
    if int(data['encryption']) == 1:
        for thing in data:
            if thing == 'encryption' or thing == 'destination' or thing == 'sender':
                pass
            else:
                data[thing] = Ciphers.XORCipher.decrypt(data[thing])
    if int(data['encryption']) == 2:
        for thing in data:
            if thing == 'encryption' or thing == 'destination' or thing == 'sender':
                pass
            else:
                data[thing] = Ciphers.AESCipher.decrypt(data[thing], '41fb5b5ae4d57c5ee528adb078ac3b2e')
    if int(data['encryption']) == 3:
        for user in listLoggedInUsers:
                if user['username'] == data['destination']:
                    data = Ciphers.RSA1024Cipher.decrypt(data, user['rsakey'])
    if int(data['encryption']) == 4:
        for user in listLoggedInUsers:
            if user['username'] == data['destination']:
                data['decryptionKey'] = Ciphers.RSA1024Cipher.decryptValue(data['decryptionKey'], user['rsakey'])
        for thing in data:
            if thing == 'encryption' or thing == 'destination' or thing == 'sender' or thing == 'decryptionKey':
                pass
            else:
                data[thing] = Ciphers.AESCipher.decrypt(data[thing], data['decryptionKey'])
        
    if 'stamp' not in data:
        data['stamp'] = int(time.time())
    if int(data['stamp']) + 31536000 < int(time.time()):
        data['stamp'] = int(time.time())
    if 'encoding' not in data:
        data['encoding'] = 2
    if 'markdown' not in data:
        data['markdown'] = 0

    if 'hashing' not in data:
        data['hashing'] = 0
    if 'hash' not in data:
        data['hash'] = ''
    
    text = ''
    salt = data['sender'].encode('ascii')
    if 'message' in data:
        data['message'] = bleach.clean(data['message'])
        text = data['message'].encode('utf-8')
    if 'file' in data:
        text = data['file']

    if int(data['hashing']) == 0:
        return data
    if int(data['hashing']) == 1:
        if SHA256.new(text).hexdigest() == data['hash']:
            return data
    if int(data['hashing']) == 2:
        if SHA256.new(text + salt).hexdigest() == data['hash']:
            return data
    if int(data['hashing']) == 3:
        if SHA512.new(text).hexdigest() == data['hash']:
            return data
    if int(data['hashing']) == 4:
        if SHA512.new(text + salt).hexdigest() == data['hash']:
            return data
    if int(data['hashing']) == 5:
        if bcrypt.verify(text, data['hash']):
            return data
    if int(data['hashing']) == 6:
        if bcrypt.verify(text + salt, data['hash']):
            return data
    if int(data['hashing']) == 7:
        if scrypt.verify(text, data['hash']):
            return data
    if int(data['hashing']) == 8:
        if scrypt.verify(text + salt, data['hash']):
            return data
    
    return str('7: Hash does not match')

def process(data, peer):
    supported = """Available APIs: \n/listAPI \n/ping \n/recieveMessage [sender] [destination] [message] [stamp(opt)] [markdown] [encoding(opt)] [encryption(opt)] [hashing(opt)] [hash(opt)]\n/recieveFile [sender] [destination] [file] [filename] [content_type] [stamp] [encryption] [hash] \nEncoding: 0, 2\nEncryption: 0\nHashing: 0"""
    try:
        if peer['username'] == 'ssit662':
            peer['ip'] = 'localhost'
        supported = urllib2.urlopen('http://' + unicode(peer['ip']) + ':' + unicode(peer['port']) + '/listAPI').read()
        supported = supported.split("\n")
    except:
        pass
    
    if '8' in supported[-1]:
        data['hashing'] = '8'
    if '7' in supported[-1]:
        data['hashing'] = '7'
    if '6' in supported[-1]:
        data['hashing'] = '6'
    if '5' in supported[-1]:
        data['hashing'] = '5'
    if '1' in supported[-1]:
        data['hashing'] = '1'
    if '2' in supported[-1]:
        data['hashing'] = '2'
    if '3' in supported[-1]:
        data['hashing'] = '3'
    if '4' in supported[-1]:
        data['hashing'] = '4'

    text = ''
    salt = data['sender'].encode('ascii')
    if 'message' in data:
        data['message'] = data['message'].encode('utf-8')
        text = data['message']
    if 'file' in data:
        text = data['file']

    if data['hashing'] == '1':
        data['hash'] = SHA256.new(text).hexdigest()
    if data['hashing'] == '2':
        data['hash'] = SHA256.new(text + salt).hexdigest()
    if data['hashing'] == '3':
        data['hash'] = SHA512.new(text).hexdigest()
    if data['hashing'] == '4':
        data['hash'] = SHA512.new(text + salt).hexdigest()
    if data['hashing'] == '5':
        data['hash'] = bcrypt.hash(text)
    if data['hashing'] == '6':
        data['hash'] = bcrypt.hash(text + salt)
    if data['hashing'] == '7':
        data['hash'] = scrypt.hash(text)
    if data['hashing'] == '8':
        data['hash'] = scrypt.hash(text + salt)
    
    if '1' in supported[-2]:
        data['encryption'] = '1'
    if '2' in supported[-2]:
        data['encryption'] = '2'
    if '3' in supported[-2]:
        data['encryption'] = '3'
    if '4' in supported[-2]:
        data['encryption'] = '4'
    
    if data['encryption'] == '1':
        for thing in data:
            if thing == 'encryption' or thing == 'destination' or thing == 'sender':
                pass
            else:
                data[thing] = Ciphers.XORCipher.encrypt(data[thing])
    if data['encryption'] == '2':
        for thing in data:
            if thing == 'encryption' or thing == 'destination' or thing == 'sender':
                pass
            else:
                data[thing] = Ciphers.AESCipher.encrypt(data[thing], '41fb5b5ae4d57c5ee528adb078ac3b2e')
    if data['encryption'] == '3':
        data = Ciphers.RSA1024Cipher.encrypt(data, peer['publicKey'])
    if data['encryption'] == '4':
        key = Ciphers.AESCipher.generateKeys()
        data['decryptionKey'] = Ciphers.RSA1024Cipher.encryptValue(key, peer['publicKey'])
        for thing in data:                  
            if thing == 'encryption' or thing == 'destination' or thing == 'sender' or thing == 'decryptionKey':
                pass
            else:
                data[thing] = Ciphers.AESCipher.encrypt(data[thing], key)

    return data