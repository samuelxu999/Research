'''
Created on Aug 5, 2019

@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: Random share based on PVSS and BFT agreement
'''
import math
from wallet import Wallet
from nodes import *
from CryptoLib.PVSS import *
from CryptoLib.crypto_rsa import Crypto_RSA
from utilities import TypesUtil
from configuration import *

class RandShare(object):
	def __init__(self):
		# Instantiate the Wallet
		self.wallet = Wallet()
		self.wallet.load_accounts()
		# Instantiate the PeerNodes
		self.peer_nodes = PeerNodes()
		self.peer_nodes.load_ByAddress()

		#get account data
		account_data = self.wallet.accounts[0]
		self.key_numbers={}
		# get key_numbers from saved account_data
		load_public_key_bytes = TypesUtil.hex_to_string(account_data['public_key'])
		load_publick_key=Crypto_RSA.load_public_key(load_public_key_bytes)

		# genereate key pairs numbers
		public_numbers = load_publick_key.public_numbers()

		# add public numbers
		self.p=public_numbers.n
		self.e=public_numbers.e
		self.key_size=load_publick_key.key_size

		# poly parameter size should be no more than key_size/2
		self.poly_max = pow(2, (self.key_size/2) )-1
		self.s = PVSS.randnt(self.poly_max)

		#set <n, t> for shares
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

	def create_shares(self):

		'''test PVSS function'''
		poly_secrets, shares = PVSS.split_shares(self.s, self.t, self.n, self.poly_max, self.p)
		json_shares={}
		json_shares['poly_secrets']=poly_secrets
		nodes = self.peer_nodes.get_nodelist()
		node_shares={}
		if shares:
			for share, node in zip(shares, nodes):
				json_node = TypesUtil.string_to_json(node)
				node_shares[json_node['address']]=share
		json_shares['node_shares']=node_shares
		return json_shares

	@staticmethod
	def save_sharesInfo(json_shares, op_type=0):
			"""
			Save the random shares information to static json file
			"""

			if(not os.path.exists(RANDOM_DATA_DIR)):
			    os.makedirs(RANDOM_DATA_DIR)
			if(op_type==0):
				FileUtil.JSON_save(RANDOM_DATA_DIR+'/'+RANDSHARE_INFO, json_shares)
			else:
				FileUtil.JSON_save(RANDOM_DATA_DIR+'/'+RANDSHARE_HOST, json_shares)

	@staticmethod
	def load_sharesInfo(op_type=0):
			"""
			load validator information from static json file
			"""
			if(os.path.isfile(RANDOM_DATA_DIR+'/'+RANDSHARE_INFO) and op_type==0):
			    return FileUtil.JSON_load(RANDOM_DATA_DIR+'/'+RANDSHARE_INFO)
			elif(os.path.isfile(RANDOM_DATA_DIR+'/'+RANDSHARE_HOST) and op_type==1):
				return FileUtil.JSON_load(RANDOM_DATA_DIR+'/'+RANDSHARE_HOST)
			else:
				return None

	def poly_commits(self, poly_secrets):
		return PVSS.get_poly_commitment(self.e, poly_secrets, self.p)

	def share_proofs(self, shares):
		return PVSS.get_share_proofs(self.e, shares, self.p)

	def verify_shares(self, poly_commits, share_proofs):
		return PVSS.verify_shares(poly_commits, share_proofs, self.p)

def test_randshare():
	myrandshare = RandShare()
	# myrandshare.print_config()
	# json_shares=myrandshare.create_shares()
	# RandShare.save_sharesInfo(json_shares)
	load_json_shares=RandShare.load_sharesInfo()
	#print(load_json_shares['node_shares']['f55af09f40768ca05505767cd013b6b9a78579c4'])


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

	#verify_S0 = PVSS.verify_S0(poly_commits, p)
	#print('verify S0:', verify_S0 == poly_commits[0])


if __name__ == '__main__':
	# test_randshare()

	pass