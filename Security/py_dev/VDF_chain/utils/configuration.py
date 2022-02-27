"""List of parameters for the system configuration. """ 

NUM_VALIDATORS = 5 					# number of validators at each checkpoint 
BOUNDED_TIME = 5 					# upper bounded time for operation cycle time
EPOCH_SIZE = 2 						# checkpoint every n blocks

MINING_SENDER = "THE BLOCKCHAIN"	# default chain network address 
MINING_REWARD = 1					# default reward for mining a new block
MINING_DIFFICULTY = 4				# PoW difficult level

COMMIT_TRANS = 2400					# Max transactions in one block

TEST_STAKE_WEIGHT = 1				# unit PoS stake weight
TEST_STAKE_SUM = 3					# Sum of PoS stakes

CHAIN_DATA_DIR = 'chaindata'		# local chain database dir
BLOCKCHAIN_DATA = "chain_db"		# local chain database file name
CHAIN_TABLE = "Block_table"			# chain data table name
CHAIN_INFO = "chain_info.json"		# chain information file name (.json)
VOTER_DATA = "voter_db"				# local voter database file name

NODE_DATA_DIR = "nodedata"			# local node database dir
PEERS_DATABASE = "peers_db"			# local peer node database file name
VERIFY_DATABASE = "nodes_db"			# local verified node database file name
NODE_TABLE = "Node_table"			# node data table name
NODE_STATICS = "static_nodes"		# statics node data file name

RANDOM_DATA_DIR = 'randomdata'							# random share data folder
RANDSHARE_INFO = "randshare_info.json"					# random PVSS node share information file name (.json)
RANDSHARE_HOST = "randshare_host.json"					# random PVSS host share information file name (.json)
RANDSHARE_RECOVERED = "randshare_recovered.json"		# random PVSS recoverd shares information file name (.json)
RANDSHARE_VOTE = "randshare_vote.json"					# random PVSS shares vote information file name (.json)
