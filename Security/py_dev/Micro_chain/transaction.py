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
import hashlib

from utilities import FileUtil, TypesUtil, DatetimeUtil
from crypto_rsa import Crypto_RSA
from wallet import Wallet


class Transaction(object):

    def __init__(self, sender_address, sender_private_key, recipient_address, value):
        self.sender_address = sender_address
        self.sender_private_key = sender_private_key
        self.recipient_address = recipient_address
        self.value = value

    def to_dict(self):
        """
        Output dict transaction data structure. 
        """
        order_dict = OrderedDict()
        order_dict['sender_address'] = self.sender_address
        order_dict['recipient_address'] = self.recipient_address
        order_dict['value'] = self.value
        return order_dict
    def to_json(self):
        """
        Output dict transaction data structure. 
        """
        return {'sender_address': self.sender_address,
                            'recipient_address': self.recipient_address,
                            'value': self.value }


    def sign(self, sk_pw):
        '''
        Sign transaction by using sender's private key and password
        '''
        try:
            private_key_byte = TypesUtil.hex_to_string(self.sender_private_key)
            private_key = Crypto_RSA.load_private_key(private_key_byte, sk_pw)

            # generate hashed transaction
            hash_data = hashlib.sha1(str(self.to_dict()).encode('utf8')).hexdigest()
            sign_value = Crypto_RSA.sign(private_key, hash_data)
        except:
            sign_value=''
        return sign_value

    @staticmethod
    def get_dict(sender_address, recipient_address, value):
        '''
        build dict transaction data structure given parameter. 
        '''
        order_dict = OrderedDict()
        order_dict['sender_address'] = sender_address
        order_dict['recipient_address'] = recipient_address
        order_dict['value'] = value
        return order_dict

    @staticmethod
    def get_json(sender_address, recipient_address, value):
        '''
        build dict transaction data structure given parameter. 
        '''
        return {'sender_address': sender_address,
                'recipient_address': recipient_address,
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
            hash_data = hashlib.sha1(str(transaction).encode('utf8')).hexdigest()
            verify_sign=Crypto_RSA.verify(publick_key,signature,hash_data)
        except:
            verify_sign=False
        return verify_sign

    @staticmethod
    def json_to_dict(list_transactions):
        # Need to make sure that the dictionary is ordered. Otherwise we'll get a different hash
        transaction_elements = ['sender_address', 'recipient_address', 'value', 'signature']
        dict_transactions = [OrderedDict((k, transaction[k]) for k in transaction_elements) 
                        for transaction in list_transactions]
        return dict_transactions

def test():
    # Instantiate the Wallet
    mywallet = Wallet()

    # load accounts
    mywallet.load_accounts()

    #list account address
    print(mywallet.list_address())

    #----------------- test transaction --------------------
    sender = mywallet.accounts[0]
    recipient = mywallet.accounts[-1]
    attacker = mywallet.accounts[1]

    # generate transaction
    sender_address = sender['address']
    sender_private_key = sender['private_key']
    recipient_address = recipient['address']
    value = 12

    mytransaction = Transaction(sender_address, sender_private_key, recipient_address, value)

    '''print(mytransaction.sender_address)
    print(mytransaction.sender_private_key)
    print(mytransaction.recipient_address)
    print(mytransaction.value)'''
    #print(mytransaction.to_dict())
    #print(mytransaction.to_json())

    # sign transaction
    sign_data = mytransaction.sign('samuelxu999')

    # verify transaction
    dict_transaction = Transaction.get_dict(mytransaction.sender_address, 
                                            mytransaction.recipient_address,
                                            mytransaction.value)
    verify_data = Transaction.verify(sender['public_key'], sign_data, dict_transaction)
    print('verify transaction:', verify_data)


if __name__ == '__main__':
    test()
    pass