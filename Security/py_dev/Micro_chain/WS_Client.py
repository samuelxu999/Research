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
from service_api import SrvAPI


def send_transaction(isBroadcast=False):
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
    value = 15

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
    #for k in dict_transaction.items():
    #    print(k)
    #print(dict_transaction)
    #print(sign_data)

    verify_data = Transaction.verify(sender['public_key'], sign_data, dict_transaction)
    #print('verify transaction:', verify_data)
    #send transaction

    transaction_data = mytransaction.to_json()
    transaction_data['signature']=TypesUtil.string_to_hex(sign_data)
    #print(transaction_data)
    if(not isBroadcast):
        json_response=SrvAPI.POST('http://localhost:8080/test/transaction/verify', 
        						transaction_data)
    else:
        json_response=SrvAPI.POST('http://localhost:8080/test/transaction/broadcast', 
                                transaction_data)
    print(json_response)

def get_transactions():
    json_response=SrvAPI.GET('http://localhost:8080/test/transactions/get')
    transactions = json_response['transactions']
    print(transactions)

def start_mining():
    json_response=SrvAPI.GET('http://localhost:8080/test/mining')
    #transactions = json_response['transactions']
    print(json_response)

def get_nodes():
    json_response=SrvAPI.GET('http://localhost:8080/test/nodes/get')
    nodes = json_response['nodes']
    print('Peer nodes:')
    for node in nodes:
        print(node)

def get_chain():
    json_response=SrvAPI.GET('http://localhost:8080/test/chain/get')
    chain_data = json_response['chain']
    chain_length = json_response['length']
    print('Chain length:', chain_length)

    # only list latest 10 blocks
    if(chain_length>10):
        for block in chain_data[-10:]:
            print(block)
    else:
        for block in chain_data:
            print(block)


if __name__ == "__main__":
    #send_transaction()

    #get_transactions()

    #start_mining()

    #get_nodes()

    #get_chain()

    pass
