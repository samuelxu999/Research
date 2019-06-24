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
from time import time

from wallet import Wallet
from nodes import PeerNodes
from transaction import Transaction
from block import Block
from validator import Validator
from consensus import POW
from utilities import TypesUtil
from service_api import SrvAPI


# Instantiate the PeerNodes
peer_nodes = PeerNodes()
peer_nodes.load_ByAddress()


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
    time_stamp = time()
    value = 15

    mytransaction = Transaction(sender_address, sender_private_key, recipient_address, time_stamp, value)

    # sign transaction
    sign_data = mytransaction.sign('samuelxu999')

    # verify transaction
    dict_transaction = Transaction.get_dict(mytransaction.sender_address, 
                                            mytransaction.recipient_address,
                                            mytransaction.time_stamp,
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
                                            transaction_data['time_stamp'],
                                            transaction_data['value'])
        
        sign_str = TypesUtil.hex_to_string(transaction_data['signature'])
        #print(dict_transaction)
        #print(sign_str)

        peer_nodes.load_ByAddress(transaction_data['sender_address'])
        sender_node = TypesUtil.string_to_json(list(peer_nodes.get_nodelist())[0])
        #print(sender_node)
        # ====================== verify transaction ==========================
        if(sender_node!={}):
            sender_pk= sender_node['public_key']
            verify_result = Transaction.verify(sender_pk, sign_str, dict_transaction)
        else:
            verify_result = False
        return verify_result

def valid_block(target_address):

    json_response=SrvAPI.GET('http://'+target_address+'/test/chain/get')
    chain_data = json_response['chain']

    # new a block to test
    last_block = chain_data[-1]
    parent_block = Block.json_to_block(last_block)

    nonce = POW.proof_of_work(last_block, [])
    new_block = Block(parent_block, [], nonce)
    new_block.print_data()

    #print(chain_data[-1])
    json_response=SrvAPI.POST('http://'+target_address+'/test/block/verify', 
                                new_block.to_json())

    return(json_response['verify_block'])


if __name__ == "__main__":
    target_address = "localhost:8080"

    #send_transaction(target_address, True)

    #get_transactions(target_address)

    #start_mining(target_address)

    #get_nodes(target_address)

    #get_chain(target_address)

    #print('Valid last_block:', valid_block(target_address))

    #print('Valid transactions:', valid_transactions(target_address))    

    pass
