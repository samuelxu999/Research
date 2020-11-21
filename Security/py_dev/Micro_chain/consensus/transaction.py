'''
========================
transaction.py
========================
Created on June.1, 2019
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide transaction implementation.
@Reference: 
'''

from collections import OrderedDict
from time import time

from utils.utilities import FileUtil, TypesUtil, DatetimeUtil, FuncUtil
from cryptolib.crypto_rsa import Crypto_RSA

class Transaction(object):

    def __init__(self, sender_address, sender_private_key, recipient_address, time_stamp, value):
        self.sender_address = sender_address
        self.sender_private_key = sender_private_key
        self.recipient_address = recipient_address
        self.time_stamp = time_stamp
        self.value = value

    def to_dict(self):
        """
        Output dict transaction data structure. 
        """
        order_dict = OrderedDict()
        order_dict['sender_address'] = self.sender_address
        order_dict['recipient_address'] = self.recipient_address
        order_dict['time_stamp'] = self.time_stamp
        order_dict['value'] = self.value
        return order_dict

    def to_json(self):
        """
        Output dict transaction data structure. 
        """
        return {'sender_address': self.sender_address,
                'recipient_address': self.recipient_address,
                'time_stamp': self.time_stamp,
                'value': self.value }


    def sign(self, sk_pw):
        '''
        Sign transaction by using sender's private key and password
        '''
        try:
            private_key_byte = TypesUtil.hex_to_string(self.sender_private_key)
            private_key = Crypto_RSA.load_private_key(private_key_byte, sk_pw)

            # generate hashed transaction
            hash_data = FuncUtil.hashfunc_sha1(str(self.to_dict()).encode('utf8'))
            sign_value = Crypto_RSA.sign(private_key, hash_data)
        except:
            sign_value=''
        return sign_value

    @staticmethod
    def get_dict(sender_address, recipient_address, time_stamp, value):
        '''
        build dict transaction data structure given parameter. 
        '''
        order_dict = OrderedDict()
        order_dict['sender_address'] = sender_address
        order_dict['recipient_address'] = recipient_address
        order_dict['time_stamp'] = time_stamp
        order_dict['value'] = value
        return order_dict

    @staticmethod
    def get_json(sender_address, recipient_address, time_stamp, value):
        '''
        build dict transaction data structure given parameter. 
        '''
        return {'sender_address': sender_address,
                'recipient_address': recipient_address,
                'time_stamp': time_stamp,
                'value': value}
    
    @staticmethod
    def verify(sender_public_key, signature, transaction):
        """
        Verify transaction by using sender's public key
        """
        try:
            public_key_byte = TypesUtil.hex_to_string(sender_public_key)
            publick_key = Crypto_RSA.load_public_key(public_key_byte)

            # generate hashed transaction
            hash_data = FuncUtil.hashfunc_sha1(str(transaction).encode('utf8'))
            verify_sign=Crypto_RSA.verify(publick_key,signature,hash_data)
        except:
            verify_sign=False
        return verify_sign

    @staticmethod
    def json_to_dict(list_transactions):
        # Need to make sure that the dictionary is ordered. Otherwise we'll get a different hash
        transaction_elements = ['sender_address', 'recipient_address', 'time_stamp', 'value', 'signature']
        dict_transactions = [OrderedDict((k, transaction[k]) for k in transaction_elements) 
                        for transaction in list_transactions]
        return dict_transactions

