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
from randshare import RandShare


# Instantiate the PeerNodes
peer_nodes = PeerNodes()
peer_nodes.load_ByAddress()

# ====================================== validator test ==================================
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
    # print(transaction_json)
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
		SrvAPI.broadcast_GET(peer_nodes.get_nodelist(), '/test/mining', True)
		json_response = {'start mining': 'broadcast'}

	print(json_response)

def start_voting(target_address, isBroadcast=False):
	if(not isBroadcast):
		json_response=SrvAPI.GET('http://'+target_address+'/test/block/vote')
	#transactions = json_response['transactions']
	else:
	#SrvAPI.broadcast(peer_nodes.get_nodelist(), {}, '/test/block/vote')
		SrvAPI.broadcast_GET(peer_nodes.get_nodelist(), '/test/block/vote', True)
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

    if( target_node=={}):
        return

    target_address = target_node['node_url']
    # print(target_address)

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

def fetch_randshare(target_address):
	# Instantiate the Wallet
	mywallet = Wallet()
	mywallet.load_accounts()
	# get host address
	json_node={}
	json_node['address'] = mywallet.accounts[0]['address']
	# print(json_node)
	json_response=SrvAPI.POST('http://'+target_address+'/test/randshare/fetch', json_node)
	return json_response

def recovered_randshare(target_address):
	json_response=SrvAPI.GET('http://'+target_address+'/test/randshare/recovered')
	return json_response

def create_randshare(target_address):
	json_response=SrvAPI.GET('http://'+target_address+'/test/randshare/create')
	return json_response

'''def save_testlog(log_data):
	#save new key files
	test_dir = 'test_results'
	if(not os.path.exists(test_dir)):
	    os.makedirs(test_dir)
	test_file = test_dir + '/' + 'exec_time.log'
	FileUtil.AddLine(test_file, log_data)'''

def Epoch_validator(target_address, tx_size, phase_delay=BOUNDED_TIME):
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

	time.sleep(phase_delay)

	# S2: start mining 
	start_time=time.time()   
	start_mining(target_address, True)
	exec_time=time.time()-start_time
	ls_time_exec.append(format(exec_time*1000, '.3f'))

	time.sleep(phase_delay)

	# S3: fix head of epoch 
	start_time=time.time()   
	check_head()
	exec_time=time.time()-start_time
	ls_time_exec.append(format(exec_time*1000, '.3f'))

	time.sleep(phase_delay)

	# S4: voting block to finalize chain
	start_time=time.time() 
	start_voting(target_address, True)
	exec_time=time.time()-start_time
	ls_time_exec.append(format(exec_time*1000, '.3f'))

	# Prepare log messgae
	str_time_exec=" ".join(ls_time_exec)
	print(str_time_exec)
	# Save to *.log file
	FileUtil.save_testlog('test_results', 'exec_time.log', str_time_exec)

# ====================================== Random share test ==================================
# request for share from peers and cache to local
def cache_fetch_share(target_address):
	# read cached randshare
	host_shares=RandShare.load_sharesInfo(1)
	if( host_shares == None):
		host_shares = {}
	fetch_share=fetch_randshare(target_address)
	for (node_name, share_data) in fetch_share.items():
		host_shares[node_name]=share_data
	# update host shares 
	RandShare.save_sharesInfo(host_shares, 1)

# verify share and proof 
def verify_share(host_address):
	# read cached randshare 
	host_shares=RandShare.load_sharesInfo(1)
	if( host_shares == None):
		host_shares = {}
	# print(host_shares)

	# get peer node information
	peer_nodes = PeerNodes()
	peer_nodes.load_ByAddress(host_address)
	json_nodes = TypesUtil.string_to_json(list(peer_nodes.get_nodelist())[0])
	# get public numbers given peer's pk
	public_numbers = RandShare.get_public_numbers(json_nodes['public_key'])

	# get share information
	shares = host_shares[host_address]
	poly_commits = shares['poly_commitments']
	share_proofs = shares['node_proofs']
	# print(poly_commits)
	# print(share_proofs)

	# instantiate RandShare to verify share proof.
	myrandshare = RandShare()
	myrandshare.p = public_numbers.n
	share_index = share_proofs[0]
	verify_S = myrandshare.verify_S(poly_commits, share_index)
	# print('verify S', share_index, ':', verify_S==share_proofs[1])
	if(verify_S==share_proofs[1]):
		host_shares[host_address]['status']=1
		# update host shares 
		RandShare.save_sharesInfo(host_shares, 1)

# request for recovered shares from peers and cache to local 
def cache_recovered_shares(target_address):
	# read cached randshare
	recovered_shares=RandShare.load_sharesInfo(2)
	if( recovered_shares == None):
		recovered_shares = {}
	host_recovered_shares=recovered_randshare(target_address)
	for (node_name, share_data) in host_recovered_shares.items():
		recovered_shares[node_name]=share_data
	# update host shares 
	RandShare.save_sharesInfo(recovered_shares, 2)

# test recovered shares
def recovered_shares(host_address):		
	# read cached randshare
	recovered_shares=RandShare.load_sharesInfo(2)
	if( recovered_shares == None):
		recovered_shares = {}
	# print(recovered_shares)

	# get peer node information
	peer_nodes = PeerNodes()
	peer_nodes.load_ByAddress(host_address)
	json_nodes = TypesUtil.string_to_json(list(peer_nodes.get_nodelist())[0])
	# get public numbers given peer's pk
	public_numbers = RandShare.get_public_numbers(json_nodes['public_key'])

	# get shares information
	shares = recovered_shares[host_address]
	# print(shares)
	# instantiate RandShare to verify share proof.
	myrandshare = RandShare()
	myrandshare.p = public_numbers.n

	secret=myrandshare.recover_secret(shares)
	# print('secret recovered from node shares:', secret)
	return secret

# test new random generator
def new_random(ls_secret):
	# get host account information
	mywallet = Wallet()
	mywallet.load_accounts()
	json_nodes=mywallet.accounts[0]
	# get public numbers given pk
	public_numbers = RandShare.get_public_numbers(json_nodes['public_key'])

	# instantiate RandShare to verify share proof.
	myrandshare = RandShare()
	myrandshare.p = public_numbers.n

	# calculate new random number
	random_secret = myrandshare.calculate_random(ls_secret)

	print(random_secret)


def Epoch_randomshare(phase_delay=BOUNDED_TIME):
	'''
	This test network latency for one epoch life time:
	'''
	# Define ls_time_exec to save executing time to log
	ls_time_exec=[]

	# get peer node information
	peer_nodes = PeerNodes()
	peer_nodes.load_ByAddress()

	# 1) create shares
	start_time=time.time()
	for peer_node in list(peer_nodes.get_nodelist()):
		json_node = TypesUtil.string_to_json(peer_node)
		create_randshare(json_node['node_url'])
	exec_time=time.time()-start_time
	ls_time_exec.append(format(exec_time*1000, '.3f'))

	time.sleep(phase_delay)

	# 2) fetch shares
	start_time=time.time()
	for peer_node in list(peer_nodes.get_nodelist()):
		json_node = TypesUtil.string_to_json(peer_node)
		cache_fetch_share(json_node['node_url'])
	exec_time=time.time()-start_time
	ls_time_exec.append(format(exec_time*1000, '.3f'))

	time.sleep(phase_delay)

	# 3) verify received shares
	start_time=time.time()
	for peer_node in list(peer_nodes.get_nodelist()):
		json_node = TypesUtil.string_to_json(peer_node)
		verify_share(json_node['address'])
	exec_time=time.time()-start_time
	ls_time_exec.append(format(exec_time*1000, '.3f'))

	time.sleep(phase_delay)

	# 4) retrive shares from peers for secret recover process
	start_time=time.time()
	for peer_node in list(peer_nodes.get_nodelist()):
		json_node = TypesUtil.string_to_json(peer_node)
		cache_recovered_shares(json_node['node_url'])
	exec_time=time.time()-start_time
	ls_time_exec.append(format(exec_time*1000, '.3f'))

	time.sleep(phase_delay)

	# 5) recover secret of each peer
	ls_secret=[]
	start_time=time.time()
	for peer_node in list(peer_nodes.get_nodelist()):
		json_node = TypesUtil.string_to_json(peer_node)
		ls_secret.append(recovered_shares(json_node['address']))
	exec_time=time.time()-start_time
	ls_time_exec.append(format(exec_time*1000, '.3f'))

	time.sleep(phase_delay)

	# 6) calculate new random
	start_time=time.time()
	new_random(ls_secret)
	exec_time=time.time()-start_time
	ls_time_exec.append(format(exec_time*1000, '.3f'))
	

	# Prepare log messgae
	str_time_exec=" ".join(ls_time_exec)
	print(str_time_exec)
	# Save to *.log file
	FileUtil.save_testlog('test_results', 'exec_time_randshare.log', str_time_exec)

if __name__ == "__main__":

	target_address = "128.226.88.210:8080"

	# |------------------------ test case type ---------------------------------|
	# | 0:set peer nodes | 1:round test | 2:single step test | 3:randshare test |
	# |-------------------------------------------------------------------------|
	op_status = 3

	if(op_status == 0):
		set_peerNodes('R2_tk_top', 1, True)
	elif(op_status == 1):
		# data_size = 2*1024*1024
		data_size = 1024
		wait_interval = 1
		test_run = 5

		for x in range(test_run):
			print("Test run:", x+1)
			Epoch_validator(target_address, data_size)
			time.sleep(wait_interval)
	elif(op_status == 2):
		# send_transaction(target_address, data_size, True)
		# get_transactions(target_address)

		# start_mining(target_address, True)

		# check_head()

		# start_voting(target_address, True)

		# get_chain(target_address, True)

		# print('Valid last_block:', test_valid_block(target_address))

		# print('Valid transactions:', test_valid_transactions(target_address)) 

		# send_vote(target_address) 
		pass  
	else:
		# host_address='ceeebaa052718c0a00adb87de857ba63608260e9'
		# cache_fetch_share(target_address)
		# verify_share(host_address)
		# cache_recovered_shares(target_address)
		# recovered_shares(host_address)
		# print(create_randshare(target_address))
		wait_interval = 1
		test_run = 5

		for x in range(test_run):
			print("Test run:", x+1)
			Epoch_randomshare()
			time.sleep(wait_interval)
		
		pass
