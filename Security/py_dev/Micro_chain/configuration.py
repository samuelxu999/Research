"""List of parameters for the system configuration. """ 

NUM_VALIDATORS = 100 # number of validators at each checkpoint 
VALIDATOR_IDS = list(range(0, NUM_VALIDATORS * 2)) # set of validators 
INITIAL_VALIDATORS = list(range(0, NUM_VALIDATORS)) # set of validators for root 
BLOCK_PROPOSAL_TIME = 100 # adds a block every 100 ticks 
EPOCH_SIZE = 5 # checkpoint every 5 blocks
AVG_LATENCY = 10  # average latency of the network (in number of ticks)

MINING_SENDER = "THE BLOCKCHAIN"
MINING_REWARD = 1
MINING_DIFFICULTY = 4

COMMIT_TRANS = 5

TEST_STAKE_WEIGHT = 1
TEST_STAKE_SUM = 3


BLOCKCHAIN_DATA = "chain_db"	# local chain database name
CHAIN_TABLE = "Block_table"		# chain data table name