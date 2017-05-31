# coding=utf8

import time
import Ciphers
from Crypto.Hash import SHA256
from Crypto.Hash import SHA512
from passlib.hash import bcrypt
from passlib.hash import scrypt
import bleach
import binascii

def unprocess(data, listLoggedInUsers):
    if 'encryption' not in data:
        data['encryption'] = 0
    
    if int(data['encryption']) == 4:
        for user in listLoggedInUsers:
            if user['username'] == data['destination']:
                data['decryptionKey'] = user['rsakey'].decrypt(binascii.unhexlify(data['decryptionKey']))

    for thing in data:
        if int(data['encryption']) == 1:
            if thing == 'encryption' or thing == 'destination' or thing == 'sender':
                pass
            else:
                data[thing] = Ciphers.XORCipher.decrypt(data[thing])
        if int(data['encryption']) == 2:
            if thing == 'encryption' or thing == 'destination' or thing == 'sender':
                pass
            else:
                data[thing] = Ciphers.AESCipher.decrypt(data[thing], '41fb5b5ae4d57c5ee528adb078ac3b2e')
        if int(data['encryption']) == 3:
            for user in listLoggedInUsers:
                if user['username'] == data['destination']:
                    if thing == 'encryption' or thing == 'destination' or thing == 'sender':
                        pass
                    else:
                        data[thing] = user['rsakey'].decrypt(binascii.unhexlify(data[thing]))
        if int(data['encryption']) == 4:                    
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
    data['message'] = bleach.clean(data['message'])

    if 'hashing' not in data:
        data['hashing'] = 0
    if 'hash' not in data:
        data['hash'] = ''
    
    if int(data['hashing']) == 0:
        return data
    if int(data['hashing']) == 1:
        if SHA256.new(data['message']).hexdigest() == data['hash']:
            return data
    if int(data['hashing']) == 2:
        if SHA256.new(data['message'] + data['sender']).hexdigest() == data['hash']:
            return data
    if int(data['hashing']) == 3:
        if SHA512.new(data['message']).hexdigest() == data['hash']:
            return data
    if int(data['hashing']) == 4:
        if SHA512.new(data['message'] + data['sender']).hexdigest() == data['hash']:
            return data
    if int(data['hashing']) == 5:
        if bcrypt.verify(data['message'], data['hash']):
            return data
    if int(data['hashing']) == 6:
        if bcrypt.verify(data['message'] + data['sender'], data['hash']):
            return data
    if int(data['hashing']) == 7:
        if scrypt.verify(data['message'], data['hash']):
            return data
    if int(data['hashing']) == 8:
        if scrypt.verify(data['message'] + data['sender'], data['hash']):
            return data
    
    return str('7: Hash does not match')