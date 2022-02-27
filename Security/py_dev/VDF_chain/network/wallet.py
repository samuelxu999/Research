'''
========================
wallet.py
========================
Created on June.1, 2019
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide wallet implementation to manage account.
@Reference: 
'''


import os
import hashlib
import json
from datetime import datetime

from cryptolib.crypto_rsa import Crypto_RSA
from utils.utilities import FileUtil, TypesUtil, DatetimeUtil

KEY_DATA_DIR = 'keystore'

class Wallet(object):

    def __init__(self, key_data_dir=KEY_DATA_DIR):        
        self.accounts = []
        self.key_data_dir = key_data_dir


    def create_account(self, sk_pw):
        """
        generate a new account based on user's password
        """
        keys_numbers = Crypto_RSA.generate_key_numbers(key_size=512)

        # use key numbers to generate PK and SK
        publick_key = Crypto_RSA.get_public_key(keys_numbers['n'], keys_numbers['e'])
        private_key = Crypto_RSA.get_private_key(keys_numbers['n'], keys_numbers['e'], keys_numbers['d'])

        # get bytes of PK and SK
        public_key_bytes = Crypto_RSA.get_public_key_bytes(publick_key)
        private_key_bytes = Crypto_RSA.get_private_key_bytes(private_key, sk_pw)

        # construct account data
        account = {'address': hashlib.sha1(public_key_bytes).hexdigest(),
                'timestamp': DatetimeUtil.datetime_timestamp(datetime.now()),
                'public_key': TypesUtil.string_to_hex(public_key_bytes),
                'private_key': TypesUtil.string_to_hex(private_key_bytes),
                'key_size': keys_numbers['key_size']}

        #save new key files
        if(not os.path.exists(self.key_data_dir)):
            os.makedirs(self.key_data_dir)
        key_file = DatetimeUtil.datetime_string(DatetimeUtil.timestamp_datetime(account['timestamp']), 
                            "UTC--%Y-%m-%d-%H-%M-%S") + '--' + account['address']
        FileUtil.JSON_save(self.key_data_dir+'/'+key_file, account)

        # append new account to list
        self.accounts.append(account)

    def load_accounts(self):
        """
        load all accounts from key files in keystore
        """
        if(os.path.exists(self.key_data_dir)):
            list_files = FileUtil.list_files(self.key_data_dir)
            for file in list_files:
                account = FileUtil.JSON_load(self.key_data_dir+'/'+file)
                self.accounts.append(account)
    
    def list_address(self):
        """
        list all account address from self.accounts
        """
        ls_address=[]
        for account in self.accounts:
            ls_address.append(account['address'])
        return ls_address

    def get_account(self, address):
        """
        get account given address
        """
        for account in self.accounts:
            if(account['address']==address):
                return account
        return None


