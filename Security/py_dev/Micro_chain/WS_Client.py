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
from nodes import PeerNodes
from transaction import Transaction
from blockchain import Blockchain
from utilities import TypesUtil
from service_api import SrvAPI


# Instantiate the PeerNodes
peer_nodes = PeerNodes()
peer_nodes.load_node()


def send_transaction(target_address, isBroadcast=False):
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

    # sign transaction
    sign_data = mytransaction.sign('samuelxu999')

    # verify transaction
    dict_transaction = Transaction.get_dict(mytransaction.sender_address, 
                                            mytransaction.recipient_address,
                                            mytransaction.value)
    #send transaction
    transaction_json = mytransaction.to_json()
    transaction_json['signature']=TypesUtil.string_to_hex(sign_data)
    #print(transaction_json)
    if(not isBroadcast):
        json_response=SrvAPI.POST('http://'+target_address+'/test/transaction/verify', 
        						transaction_json)
    else:
        json_response=SrvAPI.POST('http://'+target_address+'/test/transaction/broadcast', 
                                transaction_json)
    print(json_response)


def get_transactions(target_address):
    json_response=SrvAPI.GET('http://'+target_address+'/test/transactions/get')
    transactions = json_response['transactions']
    print(transactions)

def start_mining(target_address):
    json_response=SrvAPI.GET('http://'+target_address+'/test/mining')
    #transactions = json_response['transactions']
    print(json_response)

def get_nodes(target_address):
    json_response=SrvAPI.GET('http://'+target_address+'/test/nodes/get')
    nodes = json_response['nodes']
    print('Peer nodes:')
    for node in nodes:
        print(node)

def get_chain(target_address):
    json_response=SrvAPI.GET('http://'+target_address+'/test/chain/get')
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

def valid_transactions(target_address):
    json_response=SrvAPI.GET('http://'+target_address+'/test/chain/get')
    chain_data = json_response['chain']

    last_block = chain_data[-1]
    #print('List transactions:')
    for transaction_data in last_block['transactions']:
        #print(transaction_data)
        # ====================== rebuild transaction ==========================
        dict_transaction = Transaction.get_dict(transaction_data['sender_address'], 
                                            transaction_data['recipient_address'],
                                            transaction_data['value'])
        
        sign_str = TypesUtil.hex_to_string(transaction_data['signature'])
        #print(dict_transaction)
        #print(sign_str)

        sender_node = peer_nodes.get_node(transaction_data['sender_address'])
        #print(sender_node)
        # ====================== verify transaction ==========================
        if(sender_node!={}):
            sender_pk= sender_node['public_key']
            verify_result = Transaction.verify(sender_pk, sign_str, dict_transaction)
        else:
            verify_result = False
        return verify_result

def valid_block(target_address):
    '''json_response=SrvAPI.GET('http://localhost:8080/test/chain/get')
    chain_data = json_response['chain']
    if(len(chain_data)>1):
        return(Blockchain.valid_block(chain_data[-1], chain_data[0:-1]) )

    return False'''

    json_response=SrvAPI.GET('http://localhost:8080/test/chain/get')
    chain_data = json_response['chain']

    #print(chain_data[-1])
    json_response=SrvAPI.POST('http://localhost:8081/test/block/verify', 
                                chain_data[-1])

    print(json_response)
    return(json_response['verify_block'])


if __name__ == "__main__":
    target_address = "localhost:8080"
    
    #send_transaction(target_address, True)

    #get_transactions(target_address)

    #start_mining(target_address)

    #get_nodes(target_address)

    #print('Valid last_block:', valid_block(target_address))

    #get_chain(target_address)

    #print('Valid transactions:', valid_transactions(target_address))    

    pass
