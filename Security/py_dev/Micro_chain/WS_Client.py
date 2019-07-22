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
import time

from wallet import Wallet
from nodes import *
from transaction import Transaction
from block import Block
from vote import VoteCheckPoint
from validator import Validator
from consensus import POW
from utilities import TypesUtil, FileUtil
from service_api import SrvAPI


# Instantiate the PeerNodes
peer_nodes = PeerNodes()
peer_nodes.load_ByAddress()


def send_transaction(target_address, tx_size=1, isBroadcast=False):
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
    time_stamp = time.time()
    #value = 15
    value = TypesUtil.string_to_hex(os.urandom(tx_size))

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

def send_vote(target_address, isBroadcast=False):
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

    my_vote = VoteCheckPoint('385816343cc08cbc5350f4d1c92d2768e3be237ab364fb3bfc1dccde341205a2', 
                            'fc4341bb9867b7d389d84cd32a0e298cad595c806dd9477d0403ccc59f929138', 
                            1, 2, sender['address'])
    json_vote = my_vote.to_json()
    
    # sign vote
    sign_data = my_vote.sign(sender['private_key'], 'samuelxu999')
    json_vote['signature'] = TypesUtil.string_to_hex(sign_data)

    if(not isBroadcast):
        json_response=SrvAPI.POST('http://'+target_address+'/test/vote/verify', 
                                json_vote)
    else:
        json_response=SrvAPI.POST('http://'+target_address+'/test/vote/broadcast', 
                                json_vote)
    print(json_response)


def get_transactions(target_address):
    json_response=SrvAPI.GET('http://'+target_address+'/test/transactions/get')
    transactions = json_response['transactions']
    print(transactions)

def start_mining(target_address, isBroadcast=False):
	if(not isBroadcast):
		json_response=SrvAPI.GET('http://'+target_address+'/test/mining')
	#transactions = json_response['transactions']
	else:
		SrvAPI.broadcast_GET(peer_nodes.get_nodelist(), '/test/mining')
		json_response = {'start mining': 'broadcast'}

	print(json_response)

def start_voting(target_address, isBroadcast=False):
	if(not isBroadcast):
		json_response=SrvAPI.GET('http://'+target_address+'/test/block/vote')
	#transactions = json_response['transactions']
	else:
	#SrvAPI.broadcast(peer_nodes.get_nodelist(), {}, '/test/block/vote')
		SrvAPI.broadcast_GET(peer_nodes.get_nodelist(), '/test/block/vote')
		json_response = {'verify_vote': 'broadcast'}
	print(json_response)

def get_nodes(target_address):
    json_response=SrvAPI.GET('http://'+target_address+'/test/nodes/get')
    nodes = json_response['nodes']
    print('Peer nodes:')
    for node in nodes:
        print(node)

def add_node(target_address, json_node, isBroadcast=False):
    if(not isBroadcast):
        json_response=SrvAPI.POST('http://'+target_address+'/test/nodes/add', json_node)
        print(json_response)
    else:
        #json_response=SrvAPI.broadcast_POST(peer_nodes.get_nodelist(), json_node, '/test/nodes/add')
        for target_node in target_address:
            try:
                SrvAPI.POST('http://'+target_node+'/test/nodes/add', json_node)
            except:
                pass

def remove_node(target_address, json_node, isBroadcast=False):
    if(not isBroadcast):
        json_response=SrvAPI.POST('http://'+target_address+'/test/nodes/remove', json_node)
        print(json_response)
    else:
        #json_response=SrvAPI.broadcast_POST(peer_nodes.get_nodelist(), json_node, '/test/nodes/remove')
        for target_node in target_address:
            try:
                SrvAPI.POST('http://'+target_node+'/test/nodes/remove', json_node)
            except:
                pass

def get_chain(target_address, isDisplay=False):
	json_response=SrvAPI.GET('http://'+target_address+'/test/chain/get')
	chain_data = json_response['chain']
	chain_length = json_response['length']
	print('Chain length:', chain_length)

	if( isDisplay ):
	    # only list latest 10 blocks
	    if(chain_length>10):
	        for block in chain_data[-10:]:
	            print(block)
	    else:
	        for block in chain_data:
	            print(block)

def check_head():
	SrvAPI.broadcast_GET(peer_nodes.get_nodelist(), '/test/chain/checkhead')
	json_response = {'Reorganize processed_head': 'broadcast'}

def test_valid_transactions(target_address):
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

def test_valid_block(target_address):

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

def set_peerNodes(target_name, op_status=0, isBroadcast=False):
    #--------------------------------------- load static nodes -------------------------------------
    static_nodes = StaticNodes()
    static_nodes.load_node()

    list_address = []
    print('List loaded static nodes:')
    for node in list(static_nodes.nodes):
        #json_node = TypesUtil.string_to_json(node)
        json_node = node
        list_address.append(json_node['node_url'])
        print(json_node['node_name'] + '    ' + json_node['node_address'] + '    ' + json_node['node_url'])

    #print(list_address)

    #-------------- localhost ----------------
    target_node = static_nodes.get_node(target_name)
    target_address = target_node['node_url']
    print(target_address)

    # Instantiate the Wallet
    mywallet = Wallet()

    # load accounts
    mywallet.load_accounts()

    #list account address
    #print(mywallet.list_address())
    json_account = mywallet.get_account(target_node['node_address'])
    #print(json_account)

    # ---------------- add and remove peer node --------------------
    json_node = {}
    if(json_account!=None):
        json_node['address'] = json_account['address']
        json_node['public_key'] = json_account['public_key']
        json_node['node_url'] = target_node['node_url']
 
    if(op_status==1): 
        if(not isBroadcast):  
            add_node(target_address, json_node)
        else:
            add_node(list_address, json_node, True)
    if(op_status==2):
        if(not isBroadcast):
            remove_node(target_address, json_node)
        else:
            remove_node(list_address, json_node, True)
    
    get_nodes(target_address)

def save_testlog(log_data):
	#save new key files
	test_dir = 'test_results'
	if(not os.path.exists(test_dir)):
	    os.makedirs(test_dir)
	test_file = test_dir + '/' + 'exec_time.log'
	FileUtil.AddLine(test_file, log_data)

def Epoch_test(target_address, tx_size):
	'''
	This test network latency for one epoch life time:
	'''
	# Define ls_time_exec to save executing time to log
	ls_time_exec=[]

	#target_address = "128.226.77.51:8081"

	# S1: send test transactions
	start_time=time.time()
	send_transaction(target_address, tx_size, True)
	exec_time=time.time()-start_time
	ls_time_exec.append(format(exec_time*1000, '.3f'))

	time.sleep(BOUNDED_TIME)

	# S2: start mining 
	start_time=time.time()   
	start_mining(target_address, True)
	exec_time=time.time()-start_time
	ls_time_exec.append(format(exec_time*1000, '.3f'))

	time.sleep(BOUNDED_TIME)

	# S3: fix head of epoch 
	start_time=time.time()   
	check_head()
	exec_time=time.time()-start_time
	ls_time_exec.append(format(exec_time*1000, '.3f'))

	time.sleep(BOUNDED_TIME)

	# S4: voting block to finalize chain
	start_time=time.time() 
	start_voting(target_address, True)
	exec_time=time.time()-start_time
	ls_time_exec.append(format(exec_time*1000, '.3f'))

	# Prepare log messgae
	str_time_exec=" ".join(ls_time_exec)
	print(str_time_exec)
	# Save to *.log file
	save_testlog(str_time_exec)

if __name__ == "__main__":

	target_address = "128.226.77.51:8081"

	op_status = 1
    #data_size = 2000*1024
    data_size = 1
	if(op_status == 0):
		set_peerNodes('Desktop_Sam', 1, True)
	elif(op_status == 1):
		wait_interval = 1
		test_run = 20
		for x in range(test_run):
			print("Test run:", x+1)
			Epoch_test(target_address, data_size)
			time.sleep(wait_interval)
	else:
		#print(TypesUtil.string_to_hex(os.urandom(1000)))
		#get_transactions(target_address)

		#start_mining(target_address)

		#get_chain(target_address, True)

		#print('Valid last_block:', test_valid_block(target_address))

		#print('Valid transactions:', test_valid_transactions(target_address)) 

		#send_vote(target_address)   
		pass
	pass
