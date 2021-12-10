'''
Created on Aug 5, 2019

@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: Random share based on PVSS and BFT agreement
'''
import math
import threading
import time
import logging
from enum import Enum

from network.wallet import Wallet
from network.nodes import *
from cryptolib.PVSS import *
from cryptolib.crypto_rsa import Crypto_RSA
from utils.utilities import FileUtil, TypesUtil, DatetimeUtil
from utils.configuration import *
from utils.service_api import SrvAPI

logger = logging.getLogger(__name__)

# Define random share operation type
class RandOP(Enum):
    RandSplit = 0 
    RandDistribute = 1
    RandVote = 2
    RandRecovered = 3

class RundShare_Daemon(object):
	def __init__(self):
		# Instantiate the Wallet
		self.wallet = Wallet()
		self.wallet.load_accounts()
		
		## Instantiate the Peer Nodes management adapter
		self.peer_nodes = Nodes(db_file = PEERS_DATABASE)
		self.peer_nodes.load_ByAddress()
		
		self.randomshare_cmd = 0
		# define a thread to handle received messages by executing process_msg()
		self.randomshare_thread = threading.Thread(target=self.process_randomshare, args=())
		# Set as daemon thread
		self.randomshare_thread.daemon = True
		# Start the daemonized method execution
		self.randomshare_thread.start() 

	def set_cmd(self, randshare_cmd):
		self.randomshare_cmd = randshare_cmd

	def process_randomshare(self):
		'''
		daemon thread function: execute random share protocol
		'''
		# this variable is used as waiting time when there is no message for process.
		idle_time=0.0
		while(True):
			# ========= idle time incremental strategy, the maximum is 1 seconds ========
			if( self.randomshare_cmd==0 ):
				idle_time+=0.1
				if(idle_time>1.0):
					idle_time=1.0
				time.sleep(idle_time)
				continue
			
			# ========================== Run ramdon share protocol ==========================
			if( self.randomshare_cmd==1 ):
				logger.info("Cache fetched randshare...")

				start_time=time.time()
				# randshare_instance = RandShare()
				# 1) read cached host_shares
				host_shares=RandShare.load_sharesInfo(RandOP.RandDistribute)
				if( host_shares == None):
					host_shares = {}
				# get host address
				host_node=self.wallet.list_address()[0]
				# 2) for each peer node to fetch host share information
				for peer_node in list(self.peer_nodes.get_nodelist()):
					json_peer = TypesUtil.string_to_json(peer_node)
					# fetch_share=fetch_randshare(target_address)
					json_node={}
					json_node['address'] = host_node
					# print(json_node)
					fetch_share=SrvAPI.POST('http://'+json_peer['node_url']+'/test/randshare/fetch', json_node)

					for (node_name, share_data) in fetch_share.items():
						host_shares[node_name]=share_data
				# 3) update host shares 
				RandShare.save_sharesInfo(host_shares, RandOP.RandDistribute)
				exec_time=time.time()-start_time
				FileUtil.save_testlog('test_results', 'exec_cachefetched_shares.log', format(exec_time*1000, '.3f'))

			if( self.randomshare_cmd==2 ):
				logger.info("Cache vote randshare...")

				start_time=time.time()
				# randshare_instance = RandShare()
				# 1) read cached vote shares
				vote_shares=RandShare.load_sharesInfo(RandOP.RandVote)
				if( vote_shares == None):
					vote_shares = {}
				# 2) for each peer node to fetch vote information
				for peer_node in list(self.peer_nodes.get_nodelist()):
					json_node = TypesUtil.string_to_json(peer_node)
					# cache_vote_shares(json_node['node_url'])
					# host_vote_shares=fetchvote_randshare(json_node['node_url'])
					host_vote_shares = SrvAPI.GET('http://'+json_node['node_url']+'/test/randshare/fetchvote')
					for (node_name, share_data) in host_vote_shares.items():
						vote_shares[node_name]=share_data
				# 3) update vote shares 
				RandShare.save_sharesInfo(vote_shares, RandOP.RandVote)
				exec_time=time.time()-start_time
				FileUtil.save_testlog('test_results', 'exec_cachevote_shares.log', format(exec_time*1000, '.3f'))

			self.randomshare_cmd=0 



class RandShare(object):
	def __init__(self):
		## Instantiate the Wallet
		self.wallet = Wallet()
		self.wallet.load_accounts()

		## Instantiate the Peer Nodes management adapter
		self.peer_nodes = Nodes(db_file = PEERS_DATABASE)
		self.peer_nodes.load_ByAddress()

		## get account data
		account_data = self.wallet.accounts[0]
		self.key_numbers={}
		## get key_numbers from saved account_data
		load_public_key_bytes = TypesUtil.hex_to_string(account_data['public_key'])
		load_publick_key=Crypto_RSA.load_public_key(load_public_key_bytes)

		## genereate key pairs numbers
		public_numbers = load_publick_key.public_numbers()

		# add public numbers
		self.p=public_numbers.n
		self.e=public_numbers.e
		self.key_size=load_publick_key.key_size

		## poly parameter size should be no more than key_size/2
		self.poly_max = pow(2, (self.key_size/2) )-1
		self.s = PVSS.randnt(self.poly_max)

		## set <n, t> for shares
		nodes = self.peer_nodes.get_nodelist()
		self.n = len(nodes)
		self.t = math.ceil(2*self.n/3)

	def print_config(self):
		#list account address
		accounts = self.wallet.list_address()
		print('Current accounts:')
		if accounts:
			i=0
			for account in accounts:
			    print(i, '  ', account)
			    i+=1

		print('Peer nodes:')
		nodes = self.peer_nodes.get_nodelist()
		for node in nodes:
			json_node = TypesUtil.string_to_json(node)
			print('    ', json_node['address'] + '    ' + json_node['node_url'])

	def create_shares(self, share_secret=0):
		# split shares given share_secret
		if(share_secret!=0):
			self.s = share_secret
		poly_secrets, shares = PVSS.split_shares(self.s, self.t, self.n, self.poly_max, self.p)	

		# used to build json shares data
		json_shares={}

		# 1) get poly_secrets
		json_shares['poly_secrets']=poly_secrets
		nodes = self.peer_nodes.get_nodelist()

		# 2) get poly_commitments
		poly_commits=self.poly_commits(poly_secrets)
		ls_poly_commits=[]
		if poly_commits:
			for poly_commit in poly_commits:
				ls_poly_commits.append(poly_commit)
		json_shares['poly_commitments']=ls_poly_commits

		# 3) assign shares for peer node
		node_shares={}
		node_proofs={}
		if shares:
			for share, node in zip(shares, nodes):
				# used for calculate share_proofs
				ls_shares=[]
				ls_shares.append(list(share))
				proof = self.share_proofs(ls_shares)

				# get node json data
				json_node = TypesUtil.string_to_json(node)

				# assign node with share and proof data
				node_shares[json_node['address']]=share
				node_proofs[json_node['address']]=proof[0]
		
		json_shares['node_shares']=node_shares
		json_shares['node_proofs']=node_proofs
		return json_shares

	def fetch_randomshares(self, json_node):
		''' 
		Prepare shares data assigned to node who request them.
		return:node_shares, poly_commitments and share_proofs
		'''
		# 1) get node_shares
		load_json_shares=RandShare.load_sharesInfo()
		node_shares = load_json_shares['node_shares']

		# 2) get poly_commitments
		poly_commitments = load_json_shares['poly_commitments']

		# 3) get share_proofs
		node_proofs = load_json_shares['node_proofs']


		# 4) prepare return json_share
		json_share = {}
		if json_node['address'] in node_shares:
			json_share['poly_commitments'] = poly_commitments
			json_share['node_shares'] = node_shares[json_node['address']]
			json_share['node_proofs'] = node_proofs[json_node['address']]
			json_share['status'] = 0

		host_node=self.wallet.list_address()[0]
		shares_response = {host_node: json_share}
		return shares_response

	def verify_randomshare(self):
		''' 
		Verify received random shares from other nodes.
		Mark correct ones as 1 and save result into local.
		'''
		# 1) read cached randshare 
		host_shares=RandShare.load_sharesInfo(RandOP.RandDistribute)
		if( host_shares == None):
			host_shares = {}
		# 2) for each peer node to verify shares
		for peer_node in list(self.peer_nodes.get_nodelist()):
			json_node = TypesUtil.string_to_json(peer_node)
			# get public numbers given peer's pk
			public_numbers = RandShare.get_public_numbers(json_node['public_key'])
			host_address = json_node['address']
			# get share information
			shares = host_shares[host_address]
			poly_commits = shares['poly_commitments']
			share_proofs = shares['node_proofs']
			# print(poly_commits)
			# print(share_proofs)

			# instantiate RandShare to verify share proof.
			# myrandshare = RandShare()
			self.p = public_numbers.n
			share_index = share_proofs[0]
			verify_S = self.verify_S(poly_commits, share_index)
			# print('verify S', share_index, ':', verify_S==share_proofs[1])
			if(verify_S==share_proofs[1]):
				host_shares[host_address]['status']=1
				# update host shares 
		RandShare.save_sharesInfo(host_shares, RandOP.RandDistribute)

	def recovered_randomshare(self):
		''' 
		Prepare shares data assigned to node who request them for recovery process.
		return:node_shares, poly_commitments and share_proofs
		'''
		# 1) get node_shares
		load_json_shares=RandShare.load_sharesInfo()
		node_shares = load_json_shares['node_shares']

		# 2) get host node address
		host_node=self.wallet.list_address()[0]

		# 3) prepare return json_share
		ls_shares = []
		for (node_name, node_data) in node_shares.items():
			ls_shares.append(node_data)

		shares_response = {host_node: ls_shares}
		return shares_response

	def fetch_vote_randonshare(self):
		''' 
		prepare shares of peer for vote process
		return: verified shares status of all nodes
		'''
		# 1) get shares host
		load_json_shares=RandShare.load_sharesInfo(RandOP.RandDistribute)

		# get host node address
		host_node=self.wallet.list_address()[0]

		# prepare return json_share
		host_shares = {}
		for (node_name, node_data) in load_json_shares.items():
			host_shares[node_name]=node_data['status']
		
		shares_response = {host_node: host_shares}
		return shares_response


	@staticmethod
	def save_sharesInfo(json_shares, op_type=RandOP.RandSplit):
			"""
			Save the random shares information to static json file
			@op_type: 0-split shares; 1-distribute and verify shares; 2-recover shares
			"""

			if(not os.path.exists(RANDOM_DATA_DIR)):
			    os.makedirs(RANDOM_DATA_DIR)
			if(op_type==RandOP.RandSplit):
				FileUtil.JSON_save(RANDOM_DATA_DIR+'/'+RANDSHARE_INFO, json_shares)
			elif(op_type==RandOP.RandDistribute):
				FileUtil.JSON_save(RANDOM_DATA_DIR+'/'+RANDSHARE_HOST, json_shares)
			elif(op_type==RandOP.RandVote):
				FileUtil.JSON_save(RANDOM_DATA_DIR+'/'+RANDSHARE_VOTE, json_shares)
			elif(op_type==RandOP.RandRecovered):
				FileUtil.JSON_save(RANDOM_DATA_DIR+'/'+RANDSHARE_RECOVERED, json_shares)
			else:
				pass

	@staticmethod
	def load_sharesInfo(op_type=RandOP.RandSplit):
			"""
			load validator information from static json file
			@op_type: 0-split shares; 1-distribute and verify shares; 2-recover shares
			"""
			if(os.path.isfile(RANDOM_DATA_DIR+'/'+RANDSHARE_INFO) and op_type==RandOP.RandSplit):
			    return FileUtil.JSON_load(RANDOM_DATA_DIR+'/'+RANDSHARE_INFO)
			elif(os.path.isfile(RANDOM_DATA_DIR+'/'+RANDSHARE_HOST) and op_type==RandOP.RandDistribute):
				return FileUtil.JSON_load(RANDOM_DATA_DIR+'/'+RANDSHARE_HOST)
			elif(os.path.isfile(RANDOM_DATA_DIR+'/'+RANDSHARE_VOTE) and op_type==RandOP.RandVote):
				return FileUtil.JSON_load(RANDOM_DATA_DIR+'/'+RANDSHARE_VOTE)
			elif(os.path.isfile(RANDOM_DATA_DIR+'/'+RANDSHARE_RECOVERED) and op_type==RandOP.RandRecovered):
				return FileUtil.JSON_load(RANDOM_DATA_DIR+'/'+RANDSHARE_RECOVERED)
			else:
				return None
	@staticmethod
	def verify_vote_shares():
		# read cached randshare
		vote_shares=RandShare.load_sharesInfo(RandOP.RandVote)
		verify_vote = {}
		if( vote_shares != None):
			# For each cell in vote table to calculate vote result
			for (host_name, vote_data) in vote_shares.items():
				if(host_name not in verify_vote):
					verify_vote[host_name]=0
				for (node_name, status) in vote_data.items():
					if(node_name not in verify_vote):
						verify_vote[node_name]=0
					verify_vote[node_name]+=status
		return verify_vote

	def poly_commits(self, poly_secrets):
		return PVSS.get_poly_commitment(self.e, poly_secrets, self.p)

	def share_proofs(self, shares):
		return PVSS.get_share_proofs(self.e, shares, self.p)

	def verify_shares(self, poly_commits, share_proofs):
		return PVSS.verify_shares(poly_commits, share_proofs, self.p)

	def verify_S(self, poly_commits, share_index):
		return PVSS.verify_S(poly_commits, share_index, self.p)

	def recover_secret(self, node_shares):
		return PVSS.recover_secret(node_shares, self.p)

	def calculate_random(self, secrets):
		random_secret = 0;
		for secret in secrets:
			random_secret+=secret
			random_secret %= self.p
		return random_secret


	@staticmethod
	def get_public_numbers(hex_public_key):
		# get key_numbers from saved account_data
		load_public_key_bytes = TypesUtil.hex_to_string(hex_public_key)
		load_publick_key=Crypto_RSA.load_public_key(load_public_key_bytes)

		# genereate key pairs numbers
		return load_publick_key.public_numbers()

def test_randshare():
	myrandshare = RandShare()
	# myrandshare.print_config()
	# int_share = TypesUtil.hex_to_int('ceeebaa052718c0a00adb87de857ba63608260e9')
	# json_shares=myrandshare.create_shares(int_share)
	# RandShare.save_sharesInfo(json_shares)
	load_json_shares=RandShare.load_sharesInfo()
	#print(load_json_shares['node_shares']['f55af09f40768ca05505767cd013b6b9a78579c4'])

	if(load_json_shares==None):
		return

	''' randshare function'''	
	print('poly_secrets:')
	poly_secrets = load_json_shares['poly_secrets']
	if poly_secrets:
	    for poly_secret in poly_secrets:
	        print('  ', poly_secret)	

	print('node_shares:')
	node_shares = load_json_shares['node_shares']
	nodes = myrandshare.peer_nodes.get_nodelist()
	if node_shares:
		shares=[]
		for node in nodes:
			json_node = TypesUtil.string_to_json(node)
			shares.append(node_shares[json_node['address']])
			print('  ', node_shares[json_node['address']])

	# get poly_commits
	poly_commits = myrandshare.poly_commits(poly_secrets)
	print('poly_commitments:')
	if poly_commits:
	    for poly_commit in poly_commits:
	        print('  ', poly_commit)

	# get share_proofs
	share_proofs = myrandshare.share_proofs(shares)
	print('share_proofs:')
	share_proofs.sort(key=lambda tup: tup[0])
	if share_proofs:
	    for share_proof in share_proofs:
	        print('  ', share_proof)

	verify_shares = myrandshare.verify_shares(poly_commits, share_proofs)
	print('verify_shares:')
	if verify_shares:
	    for verify_share in verify_shares:
	        print('  ', verify_share)

	print('verify results:')
	if verify_shares:
	    for share_proof, verify_share in zip(share_proofs, verify_shares):
	        print('  ',share_proof == verify_share)

	share_index = 0
	verify_S = myrandshare.verify_S(poly_commits, share_index)
	if(share_index>0):
		print('verify S', share_index, ':', verify_S==share_proofs[share_index-1][1])
	else:
		print('verify S', share_index, ':', verify_S==poly_commits[0])

	secret=myrandshare.recover_secret(shares)
	print('secret recovered from node shares:', secret)
	print('verify recovered secret', secret==poly_secrets[0])


	ls_secret = [secret,1]
	random_secret=myrandshare.calculate_random(ls_secret)
	print('New random secret:',random_secret)
