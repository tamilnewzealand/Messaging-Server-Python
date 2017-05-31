# coding=utf8

import time
import Ciphers
from Crypto.Hash import SHA256
from Crypto.Hash import SHA512
from passlib.hash import bcrypt
from passlib.hash import scrypt
import bleach
import binascii

def unprocess(data):
    if 'encryption' not in data:
        data['encryption'] = '0'
    for thing in data:
        if data['encryption'] == '1':
            if thing == 'encryption' or thing == 'destination':
                pass
            else:
                data[thing] = Ciphers.XORCipher.decrypt(data[thing])
        if data['encryption'] == '2':
            if thing == 'encryption' or thing == 'destination':
                pass
            else:
                data[thing] = Ciphers.AESCipher.decrypt(data[thing])
        if data['encryption'] == '3':
            if thing == 'encryption' or thing == 'destination':
                pass
            else:
                if len(unicode(data[thing])) > 256:
                    text = data[thing]
                    n = 256
                    [text[i:i+n] for i in range(0, len(text), n)]
                    for block in text:
                        block = rsakey.decrypt(binascii.unhexlify(block))
                    data[thing] = ''.join(text)
                else:
                    data[thing] = rsakey.decrypt(binascii.unhexlify(data[thing]))
    
    if 'stamp' not in data:
        data['stamp'] = int(time.time())
    if int(data['stamp']) + 31536000 < int(time.time()):
        data['stamp'] = int(time.time())
    if 'encoding' not in data:
        data['encoding'] = '2'
    if 'markdown' not in data:
        data['markdown'] = '0'
    data['message'] = bleach.clean(data['message'])

    if 'hashing' not in data:
        data['hashing'] = '0'
    if 'hash' not in data:
        data['hash'] = ''
    
    if data['hashing'] == '0':
        return data
    if data['hashing'] == '1':
        if SHA256.new(data['message']).hexdigest() == data['hash']:
            return data
    if data['hashing'] == '2':
        if SHA256.new(data['message'] + data['sender']).hexdigest() == data['hash']:
            return data
    if data['hashing'] == '3':
        if SHA512.new(data['message']).hexdigest() == data['hash']:
            return data
    if data['hashing'] == '4':
        if SHA512.new(data['message'] + data['sender']).hexdigest() == data['hash']:
            return data
    if data['hashing'] == '5':
        if bcrypt.verify(data['message'], data['hash']):
            return data
    if data['hashing'] == '6':
        if bcrypt.verify(data['message'] + data['sender'], data['hash']):
            return data
    if data['hashing'] == '7':
        if scrypt.verify(data['message'], data['hash']):
            return data
    if data['hashing'] == '8':
        if scrypt.verify(data['message'] + data['sender'], data['hash']):
            return data
    
    return str('7: Hash does not match')