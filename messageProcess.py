# coding=utf8

import time
import Ciphers
from Crypto.Hash import SHA256
from Crypto.Hash import SHA512
from passlib.hash import bcrypt
from passlib.hash import scrypt

def unprocess(data):
    if 'stamp' not in data:
        data['stamp'] = int(time.time())
    if int(data['stamp']) + 31536000 < int(time.time()):
        data['stamp'] = int(time.time())
    if 'encoding' not in data:
        data['encoding'] = '0'
    if 'encryption' not in data:
        data['encryption'] = '0'
    
    for thing in data:
        if data['encryption'] == '1':
            if thing == data['encryption'] or thing == data['destination']:
                pass
            else:
                thing = Ciphers.XORCipher.decrypt(thing)
        if data['encryption'] == '2':
            if thing == data['encryption'] or thing == data['destination']:
                pass
            else:
                thing = Ciphers.AESCipher.decrypt(thing)
        if data['encryption'] == '3':
            if thing == data['encryption'] or thing == data['destination']:
                pass
            else:
                thing = Ciphers.RSA1024Cipher.decrypt(thing)
        if data['encoding'] == '0':
            thing = thing.decode('ascii')
        if data['encoding'] == '1':
            thing = thing.decode('cp-1252')
        if data['encoding'] == '2':
            thing = thing.decode('utf-8')
        if data['encoding'] == '3':
            thing = thing.decode('utf-16')
    
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