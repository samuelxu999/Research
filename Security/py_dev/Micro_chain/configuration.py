"""List of parameters for the system configuration. """ 

NUM_VALIDATORS = 3 					# number of validators at each checkpoint 
EPOCH_SIZE = 2 						# checkpoint every n blocks

MINING_SENDER = "THE BLOCKCHAIN"	# default chain network address 
MINING_REWARD = 1					# default reward for mining a new block
MINING_DIFFICULTY = 4				# PoW difficult level

COMMIT_TRANS = 5					# Max transactions in one block

TEST_STAKE_WEIGHT = 1				# unit PoS stake weight
TEST_STAKE_SUM = 3					# Sum of PoS stakes

CHAIN_DATA_DIR = 'chaindata'		# local chain database dir
BLOCKCHAIN_DATA = "chain_db"		# local chain database file name
CHAIN_TABLE = "Block_table"			# chain data table name
CHAIN_INFO = "chain_info.json"		# chain information file name (.json)
VOTER_DATA = "voter_db"				# local voter database file name

NODE_DATA_DIR = "nodedata"			# local node database dir
NODE_DATABASE = "node_db"			# local node database file name
NODE_TABLE = "Node_table"			# node data table name
NODE_STATICS = "static_nodes"		# statics node data file name
