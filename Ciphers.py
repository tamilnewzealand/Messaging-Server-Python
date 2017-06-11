# coding=utf8

"""   
    Peer to Peer Chat Application
    
    Copyright (C) 2017 Sakayan Sitsabesan <ssit662@aucklanduni.ac.nz>
    
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
 """

import base64
import hashlib
import binascii
import urllib
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Cipher import XOR
from Crypto.PublicKey import RSA


class AESCipher(object):

    """
        Generates a new AES cipher key randomly.
    """
    @staticmethod
    def generateKeys():
        return binascii.hexlify(Random.new().read(16))

    """
        Encrypts the message using the supplied AES key.
    """
    @staticmethod
    def encrypt(raw, aeskey):
        raw = AESCipher._pad(raw)
        iv = Random.new().read(16)
        cipher = AES.new(aeskey, AES.MODE_CBC, iv)
        return urllib.quote(binascii.hexlify(iv + cipher.encrypt(raw)), safe='')

    """
        Decrypts the message using the supplied AES key.
    """
    @staticmethod
    def decrypt(enc, aeskey):
        enc = binascii.unhexlify(enc)
        iv = enc[:16]
        cipher = AES.new(aeskey, AES.MODE_CBC, iv)
        return cipher.decrypt(enc[16:]).rstrip(' ')

    """
        Pads the message with spaces to reach the block size.
    """
    @staticmethod
    def _pad(s):
        return s + (16 - len(s) % 16) * chr(32)

    """
        Pads the message with spaces.
    """
    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s) - 1:])]


class XORCipher():

    """
        Decrypts the message using the hard coded XOR key.
    """
    @staticmethod
    def decrypt(text):
        key = XOR.new('01101001')
        return key.decrypt(binascii.unhexlify(text))

    """
        Encrypts the message using the hard coded XOR key.
    """
    @staticmethod
    def encrypt(text):
        key = XOR.new('01101001')
        return binascii.hexlify(key.encrypt(text))


class RSA1024Cipher():

    """
        Generates a new RSA1024 cipher key randomly.
    """
    @staticmethod
    def generatekeys():
        random_generator = Random.new().read
        key = RSA.generate(1024, random_generator)
        return key

    """
        Encrypts the data dictionary using the supplied RSA key.
    """
    @staticmethod
    def encrypt(data, key):
        pubkey = RSA.importKey(binascii.unhexlify(key))
        for thing in data:
            if thing == 'encryption' or thing == 'destination' or thing == 'sender':
                pass
            else:
                data[thing] = binascii.hexlify(
                    pubkey.encrypt(data[thing], 32)[0])
        data['encryption'] = 3
        return data

    """
        Encrypts the message using the supplied RSA key.
    """
    @staticmethod
    def encryptValue(value, key):
        pubkey = RSA.importKey(binascii.unhexlify(key))
        return binascii.hexlify(pubkey.encrypt(value, 32)[0])

    """
        Decrypts the data dictionary using the supplied RSA key.
    """
    @staticmethod
    def decrypt(data, key):
        for thing in data:
            if thing == 'encryption' or thing == 'destination' or thing == 'sender':
                pass
            else:
                data[thing] = key.decrypt(binascii.unhexlify(data[thing]))
        return data

    """
        Decrypts the message using the supplied RSA key.
    """
    @staticmethod
    def decryptValue(value, key):
        return key.decrypt(binascii.unhexlify(value))
