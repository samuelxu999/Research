import time
import logging
import argparse
import sys
import os

from wrapper_pyca import Crypto_DSA, Crypto_Hash
from utilities import FileUtil, TypesUtil
from service_utils import TenderUtils

LOG_INTERVAL = 25

logger = logging.getLogger(__name__)

#global variable

def define_and_get_arguments(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description="Run websocket client test."
    )

    parser.add_argument("--test_func", type=int, default=0, 
                        help="Execute test function: 0-function test, \
                        							1-Asyn_KeyGen(), \
                        							2-ENF_test()")
    parser.add_argument("--tx_round", type=int, default=1, help="tx evaluation round")
    parser.add_argument("--wait_interval", type=int, default=1, 
                        help="break time between tx evaluate step.")
    parser.add_argument("--keygen_op", type=int, default=0, 
                        help="Asyn_KeyGen operation: 0-Generate key pairs, \
                        							1-Load key pairs, then Sign and verify test.")
    parser.add_argument("--query_tx", type=int, default=0, 
                        help="Query tx or commit tx: 0-Query, 1-Commit")
    args = parser.parse_args(args=args)
    return args

def ENF_test(args):
	ENF_file = "./data/ENF_sample.log"
	for i in range(args.tx_round):
		logger.info("Test run:{}".format(i+1))
		# -------------------------- Tendermint test ----------------------------------
		if(args.query_tx==0):
			# verify hash model
			logger.info("Verify ENF: '{}' --- {}\n".format(ENF_file, 
			                                            TenderUtils.verify_ENF(ENF_file)) )
		else:
			# call tx_evaluate() and record tx_commit time
			logger.info("Tx commit ENF '{}' --- {}\n".format(ENF_file, 
			                                            TenderUtils.tx_evaluate(ENF_file)))
		time.sleep(args.wait_interval)

def Asyn_KeyGen(args):
	logger.info('Asyn_KeyGen() running...')
	if(args.keygen_op==0):
		logger.info('Generate key pairs')
		key_pairs = Crypto_DSA.generate_key_pairs()
		# Crypto_DSA.display_key_pairs(key_pairs)

		public_key = Crypto_DSA.get_public_key(key_pairs['public_key'])
		# logger.info(public_key.public_numbers())

		private_key = Crypto_DSA.get_private_key(key_pairs['private_key'], public_key)
		# logger.info(private_key.private_numbers().x)

		public_key_bytes = Crypto_DSA.get_public_key_bytes(public_key)
		logger.info(public_key_bytes)

		private_key_bytes = Crypto_DSA.get_private_key_bytes(private_key, encryp_pw=b'samuelxu999')
		logger.info(private_key_bytes)

		# save key bytes to files
		Crypto_DSA.save_key_bytes(public_key_bytes, 'public_key_file')
		Crypto_DSA.save_key_bytes(private_key_bytes, 'private_key_file')

	else:
		logger.info('Load key pairs')

		load_public_key_bytes = Crypto_DSA.load_key_bytes('public_key_file')
		load_private_key_bytes = Crypto_DSA.load_key_bytes('private_key_file')

		reload_public_key = Crypto_DSA.load_public_key_bytes(load_public_key_bytes)
		logger.info(reload_public_key.public_numbers())

		reload_private_key = Crypto_DSA.load_private_key_bytes(load_private_key_bytes, encryp_pw=b'samuelxu999')
		logger.info(reload_private_key.private_numbers().x)

		# logger.info('Sign and verify test')
		#sing message
		message_data = b'samuel'
		sign_value = Crypto_DSA.sign(reload_private_key, message_data)

		# #verify signature
		verify_sign=Crypto_DSA.verify(reload_public_key,sign_value,message_data)
		logger.info("Sign verification: {}".format(verify_sign))



if __name__ == "__main__":
	# Logging setup
	FORMAT = "%(asctime)s | %(message)s"
	logging.basicConfig(format=FORMAT)
	logger.setLevel(level=logging.DEBUG)

	serviceUtils_logger = logging.getLogger("service_utils")
	serviceUtils_logger.setLevel(logging.INFO)

	args = define_and_get_arguments()

	if(args.test_func==1):
		Asyn_KeyGen(args)
	elif(args.test_func==2):
		ENF_test(args)
	else:
		pass
