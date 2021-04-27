# Fed-DDM Project
Official implementation of paper "Fed-DDM: A Federated Ledgers based Framework for Hierarchical Decentralized Data Marketplaces". Please refer to article online: [https://arxiv.org/abs/2104.05583](https://arxiv.org/abs/2104.05583) for detail.

## Developing environment
For Ethereum private network configuration, please refer to [link](https://github.com/samuelxu999/Blockchain_dev/tree/master/MyChains).

For smart contract development, please refer to [Truffle](https://truffleframework.com/docs) for truffle environment setup and usage. The demo application is developed by python and Flask.

## Microservices implementation
The concept proof system is deployed and run on a microservices SOA framework. You can access microservices projects reousrce on github: 
[AuthID](https://github.com/samuelxu999/Microservices_dev/tree/master/Services_dev/AuthID); 
[BlendCAC](https://github.com/samuelxu999/Microservices_dev/tree/master/Services_dev/BlendCAC); 
[IndexAuth](https://github.com/samuelxu999/Microservices_dev/tree/master/Services_dev/IndexAuth);
[FedDDM](https://github.com/samuelxu999/Microservices_dev/tree/master/Services_dev/FedDDM).


## Fed-DDM Core
The key components are implemented as seperate library modules to support server and client apps.

### contract_dev
This is truffle folder to develop smart contract for TB service exchange implementation.
* contract:

	--- SrvExchange.sol: Service exchange contract to support inter-ledger transaction, like broker deligation, tx querying and committed.
	
	--- Migrations.sol: This is a separate Solidity file that manages and updates the status of your deployed smart contract. This file comes with every Truffle project, and is usually not edited.
	
* migrations:

	--- 1_initial_migration.js: This file is the migration (deployment) script for the Migrations contract found in the Migrations.sol file.
	
	--- 2_deploy_contracts.js: This file is the migration (deployment) script for deploying our developed smart contract Solidity files.
	

### src
The prototype desgin of Fed-DDM by using python. The functions are mainly for back-end servie API and blockchain operations.

* configuration:

	--- addr_list.json: This json file records all participants' account address used in prototype.

	--- services_list.json: This json file saves deployed micorservice nodes' IP address used in prototype.

* libs:

	--- account: provides transaction data strucutre for intra-ledger (transaction.py) and support account management based on RAS algorithm.

	--- cryptolib: supports cryptography primitives, like RSA, PVSS and VRF, implementations.

	--- utils: utilities and tools to support core functions, like RPC wrappers for inter-ledger and intra-ledger interaction (Tender_RPC.py and brokerClient_RPC.py), Interface of smart contract (SrvExchangeToken.py), and web service APIs for front-end apps (brokerClient_RPC.py and service_utils.py)

* apps:
	---  Test_Client.py: works as client node to interact with broker_servers and nodes in intra-ledger.

	--- Broker_Server.py.py: This module provide encapsulation of RestFul web-service API that handle and response client's request.

### test
    * Test data and logs

	* Performance_Test.py: This module defines test cases to evaluate performance, and visualize data for analysis.
