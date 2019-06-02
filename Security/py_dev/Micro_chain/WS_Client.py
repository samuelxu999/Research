#!/usr/bin/env python

'''
========================
WS_Client module
========================
Created on Nov.2, 2017
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide encapsulation of client API that access to Web service.
'''

import requests
import json

from wallet import Wallet
from transaction import Transaction
from utilities import TypesUtil

class WSClient(object):
	'''
	Post data to add record
	'''
	@staticmethod
	def send_transaction(api_url, transaction):          
		headers = {'Content-Type' : 'application/json'}
		response = requests.post(api_url, data=json.dumps(transaction), headers=headers)

		#get response json
		json_response = response.json()      

		return json_response

def test_transaction():
    # Instantiate the Wallet
    mywallet = Wallet()

    # load accounts
    mywallet.load_accounts()

    #list account address
    #print(mywallet.list_address())

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

    # sign transaction
    sign_data = mytransaction.sign('samuelxu999')

    # verify transaction
    dict_transaction = Transaction.get_dict(mytransaction.sender_address, 
                                            mytransaction.recipient_address,
                                            mytransaction.value)
    for k in dict_transaction.items():
        print(k)
    #print(dict_transaction)
    #print(sign_data)

    verify_data = Transaction.verify(sender['public_key'], sign_data, dict_transaction)
    #print('verify transaction:', verify_data)
    #send transaction

    transaction_data = mytransaction.to_json()
    transaction_data['signature']=TypesUtil.string_to_hex(sign_data)
    #print(transaction_data)
    json_response=WSClient.send_transaction('http://localhost:8042/test/transaction', 
    						transaction_data)

    print(json_response)



if __name__ == "__main__":
	test_transaction()
	pass
