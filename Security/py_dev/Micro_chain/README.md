# Microchain
Official implementation of article "BMicrochain: A hybrid consensus mechanism for lightweight distributed ledger for iot. Please refer to online: [link](https://arxiv.org/abs/1909.10948) for detail.

The overview of project organization are:

## Microchain Core 
The key components are implemented as seperate library modules to support server and client apps.

* libs:

	--- consensus: provides key consensus algorithms and validator implementation. Data structure like transaction, block and vote, are also included.

	--- cryptolib: cryptography primitives, like RSA, PVSS and VRF, implementations.

	--- network: manages network nodes and accounts.
	
	--- randomness: generates global randomness string for committee election.

	--- utils: utilities and tools to support core functions.
	
* apps:

	--- WS_Client.py: works as client node to interact with validators.
	
	--- WS_Server.py: runs as validator who provides RESTfull webservice API for client.
	
## Test functions
The test code to verify functions in prototype impelmentation. 
* test.py: This module provides test cases top demonstrate function usage in core libs.

* test_merklelib.py: demonstrates how to use key functions in merklelib.

* static-nodes.json: This json file records all participants' account address used in prototype.

* setup_localtest.sh: is a tool to initialize localtest nodes.

## Test results
The experimental results log and performance evaluation and visualization tool.
* Performance_Test.py: This module provide API functions to support data processing and results visualization.

## Environment setup
* env_setup.txt: Environment setup instruction.

* requirements.txt: python dependencies used in prototype.

## Run a validator
1) New an account, run test_Wallet() in test.py

2) launch a validator: python3.X WS_Server.py --debug --blockepoch 5 --pauseepoch 3 --phasedelay 2 -p 8080




