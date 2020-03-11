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

	@staticmethod
	def save_sharesInfo(json_shares, op_type=0):
			"""
			Save the random shares information to static json file
			@op_type: 0-split shares; 1-distribute and verify shares; 2-recover shares
			"""

			if(not os.path.exists(RANDOM_DATA_DIR)):
			    os.makedirs(RANDOM_DATA_DIR)
			if(op_type==0):
				FileUtil.JSON_save(RANDOM_DATA_DIR+'/'+RANDSHARE_INFO, json_shares)
			elif(op_type==1):
				FileUtil.JSON_save(RANDOM_DATA_DIR+'/'+RANDSHARE_HOST, json_shares)
			elif(op_type==2):
				FileUtil.JSON_save(RANDOM_DATA_DIR+'/'+RANDSHARE_RECOVERED, json_shares)
			else:
				pass

	@staticmethod
	def load_sharesInfo(op_type=0):
			"""
			load validator information from static json file
			@op_type: 0-split shares; 1-distribute and verify shares; 2-recover shares
			"""
			if(os.path.isfile(RANDOM_DATA_DIR+'/'+RANDSHARE_INFO) and op_type==0):
			    return FileUtil.JSON_load(RANDOM_DATA_DIR+'/'+RANDSHARE_INFO)
			elif(os.path.isfile(RANDOM_DATA_DIR+'/'+RANDSHARE_HOST) and op_type==1):
				return FileUtil.JSON_load(RANDOM_DATA_DIR+'/'+RANDSHARE_HOST)
			elif(os.path.isfile(RANDOM_DATA_DIR+'/'+RANDSHARE_RECOVERED) and op_type==2):
				return FileUtil.JSON_load(RANDOM_DATA_DIR+'/'+RANDSHARE_RECOVERED)
			else:
				return None

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


if __name__ == '__main__':
	# test_randshare()

	pass