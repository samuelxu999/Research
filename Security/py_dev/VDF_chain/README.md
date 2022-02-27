# VDFchain
Official implementation of VDF based blockchain for IoT.

The overview of project organization are:

## VDFchain Core 
The key components are implemented as seperate library modules to support server and client apps.

* libs:

	--- consensus: provides key consensus algorithms and validator implementation. Data structure like transaction, block and vote, are also included.

	--- cryptolib: cryptography primitives, like RSA, PVSS and VRF, implementations.

	--- network: manages network nodes and accounts.
	
	--- randomness: generates global randomness string for committee election.

	--- utils: utilities and tools to support core functions.
	
* apps:

	--- VDFchain_Client.py: works as client node to interact with validators.
	
	--- VDFchain_Server.py: runs as validator who provides RESTfull webservice API for client.
	
## Test functions
The test code to verify functions in prototype impelmentation. 
* test.py: This module provides test cases top demonstrate function usage in core libs.

* static-nodes.json: This json file records all participants' account address used in prototype.

* setup_localtest.sh: is a tool to initialize localtest nodes.


## Environment setup
* env_setup.txt: Environment setup instruction.

* requirements.txt: python dependencies used in prototype.

## Run a validator
1) launch a bootstrap node: VDFchain_Server.py --debug --blockepoch 5 --pauseepoch 3 --phasedelay 2 --firstnode --save_state 60

2) launch a validator: python3.X VDFchain_Server.py --debug --blockepoch 5 --pauseepoch 3 --phasedelay 2 -p 8080 --rp 30180 --refresh_neighbors 15




