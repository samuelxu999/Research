#This is used for test code

from network.wallet import Wallet
from network.nodes import *
from consensus.transaction import Transaction
from consensus.block import Block
from consensus.validator import Validator
from consensus.consensus import *
from consensus.vote import VoteCheckPoint
from utils.utilities import FileUtil, TypesUtil
from utils.configuration import *
from utils.db_adapter import DataManager
from cryptolib.PVSS import *
from cryptolib.crypto_rsa import Crypto_RSA
from cryptolib.efficient_vdf import E_VDF

import time
import random
import copy

def build_transaction():
	# Instantiate the Wallet
	mywallet = Wallet()

	# load accounts
	mywallet.load_accounts()

	#----------------- test transaction --------------------
	sender = mywallet.accounts[0]
	recipient = mywallet.accounts[0]
	attacker = mywallet.accounts[0]

	# generate transaction
	sender_address = sender['address']
	sender_private_key = sender['private_key']
	recipient_address = recipient['address']
	time_stamp = time.time()
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

	return transaction_json

def test_PoW():
	"""
	Mining task to find new block
	"""
	root_block=Block()
	chain_data = []
	chain_data.append(root_block.to_json())

	last_block = chain_data[-1]
	#print(last_block)
	parent_block = Block.json_to_block(last_block)

	transaction_json = build_transaction()

	## convert to a order-dict transactions list
	dict_transactions = Transaction.json_to_dict([transaction_json])

	## a) ---------- calculate merkle tree root hash of dict_transactions ------
	merkle_root = FuncUtil.merkle_root(dict_transactions)

	# mining new block
	nonce = POW.proof_of_work(last_block, merkle_root)
	new_block = Block(parent_block, merkle_root, [transaction_json], nonce)
	new_block.print_data()

	chain_data.append(new_block.to_json())

	print(chain_data)


def test_PoS():
	# test PoS
	root_block=Block()
	chain_data = []
	chain_data.append(root_block.to_json())

	last_block = chain_data[-1]
	print(last_block)
	print('get proof value:', POS.get_proof(Transaction.json_to_dict(last_block['transactions']), last_block['previous_hash'], last_block['nonce'],TEST_STAKE_SUM))
	
	sum_hit = 0
	test_run = 1000
	ran_nonce = random.randint(1, 2**256)

	transaction_json = build_transaction()
	## convert to a order-dict transactions list
	dict_transactions = Transaction.json_to_dict([transaction_json])

	## a) ---------- calculate merkle tree root hash of dict_transactions ------
	merkle_root = FuncUtil.merkle_root(dict_transactions)

	for n in range(1, test_run):
		i=1
		while(POS.proof_of_stake(last_block, merkle_root, ran_nonce, TEST_STAKE_WEIGHT, TEST_STAKE_SUM )==0):
			i+=1
		#print('Try %d until succeed!' %(i))
		sum_hit+=i
	print('hit rate:', sum_hit/test_run)	


# this function show basic VSS function.
def VSS_demo():
	_PRIME = 2**511 - 1
	_PRIME_EXP = 65537	
	keys_numbers = Crypto_RSA.generate_key_numbers(_PRIME_EXP, 512)
	#print(keys_numbers)
	p = keys_numbers['n']
	s = PVSS.randnt(_PRIME)
	poly_max = _PRIME
	t = 3
	n = 6
	
	'''test PVSS function'''
	secret, shares = PVSS.split_shares(s, t, n, poly_max, p)

	print('secret:                                                     ',
	      secret[0])
	print('shares:')
	if shares:
	    for share in shares:
	        print('  ', share)

	print('secret recovered from minimum subset of shares:             ',
	      PVSS.recover_secret(shares[:t], p))
	print('secret recovered from a different minimum subset of shares: ',
	      PVSS.recover_secret(shares[-(t):], p))
	print('Verify recovered secret:', PVSS.recover_secret(shares[:t], p) == s )


def test_PVSS():

	# choose RSA key source 0: From RSA key generator; 1:From saved key_bytes files
	RSA_key_src = 1
	key_numbers={}

	if(RSA_key_src==0):
		#A) From RSA key generator
		key_numbers = Crypto_RSA.generate_key_numbers(65537, 512)
	else:
		#B) From saved key_bytes files
		# get key data from wallet
		# Instantiate the Wallet
		mywallet = Wallet()

		# load accounts
		mywallet.load_accounts()	

		#get account data
		account_data = mywallet.accounts[0]
		#key_numbers = get_public_numbers_from_files()
		load_public_key_bytes = TypesUtil.hex_to_string(account_data['public_key'])
		load_publick_key=Crypto_RSA.load_public_key(load_public_key_bytes)

		# genereate key pairs numbers
		public_numbers = load_publick_key.public_numbers()

		# add public numbers
		key_numbers['n']=public_numbers.n
		key_numbers['e']=public_numbers.e
		key_numbers['key_size']=load_publick_key.key_size

	print(key_numbers)
	p = key_numbers['n']
	e = key_numbers['e']

	# poly parameter size should be no more than key_size/2
	poly_max = pow(2, (key_numbers['key_size']/2) )-1
	s = PVSS.randnt(poly_max)
	t = 4
	n = 6

	'''test PVSS function'''
	poly_secrets, shares = PVSS.split_shares(s, t, n, poly_max, p)
	print('poly_secrets:')
	if poly_secrets:
	    for poly_secret in poly_secrets:
	        print('  ', poly_secret)	        
	print('shares:')
	if shares:
	    for share in shares:
	        print('  ', share)

	# Use e as G to construct commitment and verification
	poly_commits = PVSS.get_poly_commitment(e, poly_secrets, p)
	print('poly_commitments:')
	if poly_commits:
	    for poly_commit in poly_commits:
	        print('  ', poly_commit)

	share_proofs = PVSS.get_share_proofs(e, shares, p)
	print('share_proofs:')
	if share_proofs:
	    for share_proof in share_proofs:
	        print('  ', share_proof)

	verify_shares = PVSS.verify_shares(poly_commits, share_proofs, p)
	print('verify_shares:')
	if verify_shares:
	    for verify_share in verify_shares:
	        print('  ', verify_share)

	print('verify results:')
	if verify_shares:
	    for share_proof, verify_share in zip(share_proofs, verify_shares):
	        print('  ',share_proof == verify_share)

	verify_S0 = PVSS.verify_S(poly_commits, 0, p)
	print('verify S0:', verify_S0 == poly_commits[0])

def vdf_test():
	## initialize E_VDF instance eVDF
	eVDF=E_VDF()

	ls_time = []
	int_lambda =  256
	int_k = 128
	tau = 22
	int_tau_exp = 2**tau
	eVDF.set_up(int_lambda, int_k)

	## 1) generate big prime N
	start_time=time.time()	
	mpz_N = eVDF.generate_N()
	exec_time=time.time()-start_time
	ls_time.append(exec_time)
	print('eVDF set_up: lambda: {} \t k: {} \t N: {}\n'.format(eVDF._lambda, eVDF._k, mpz_N))

	## 2) evaluate and proof process
	x = "This text for vdf test."
	print('Test message: {}'.format(x))

	start_time=time.time()	
	proof_pair = eVDF.evaluate_proof(x, int_tau_exp, mpz_N)
	exec_time=time.time()-start_time
	ls_time.append(exec_time)
	print('eVDF evaluate_proof: tau_exp-2^{}\t pi: {} \t l: {}\n'.format(tau, proof_pair[0], proof_pair[1]))

	## convert to hex proof pairs
	hex_proof_pair=[TypesUtil.mpz_to_hex(proof_pair[0]), TypesUtil.mpz_to_hex(proof_pair[1])]
	print('eVDF hex_proof: pi: {} \t l: {}\n'.format(hex_proof_pair[0], hex_proof_pair[1]))

	## convert hex proof pairs to mpz_proof_pair
	mpz_proof_pair=[TypesUtil.hex_to_mpz(hex_proof_pair[0]), TypesUtil.hex_to_mpz(hex_proof_pair[1])]
	print('eVDF mpz_proof: pi: {} \t l: {}\n'.format(mpz_proof_pair[0], mpz_proof_pair[1]))

	## 2) verify proof process
	start_time=time.time()
	proof_verify = eVDF.verify_proof(x, int_tau_exp, mpz_N, mpz_proof_pair)
	exec_time=time.time()-start_time
	ls_time.append(exec_time)
	print('eVDF verify_proof: tau_exp-2^{}\t result: {}\n'.format(tau, proof_verify))

	print('Exec time: {}\n'.format(ls_time))

if __name__ == '__main__':
	# test_PoW()
	# test_PoS()
	# VSS_demo()
	# test_PVSS()
	# vdf_test()
	pass


