# BlendSPS
Official implementation of paper "BlendSPS: A BLockchain-ENabled Decentralized Smart Public Safety System". Please refer to archive: [https://www.preprints.org/manuscript/202007.0667/v1](https://www.preprints.org/manuscript/202007.0667/v1) for detail.

The concept proof system is deployed and run on a microservice SOA framework. You can access microservice projects reousrce on github: 
[AuthID](https://github.com/samuelxu999/Microservices_dev/tree/master/Services_dev/AuthID); 
[BlendCAC](https://github.com/samuelxu999/Microservices_dev/tree/master/Services_dev/BlendCAC); 
[IndexAuth](https://github.com/samuelxu999/Microservices_dev/tree/master/Services_dev/IndexAuth).


The overview of project organization are:

## contract_dev
The truffle project folder to develop smart contracts that work as a underlying contract layer on Ethereum blockchain network.

* contract:

	--- AuthToken.sol: smart contract for security service AuthID, an ideitity authentication mechanism.

	--- CapACToken.sol: smart contract for security service BlendCAC, an Capability-based AC mechanism.

	--- IndexToken.sol: smart contract for security service IndexAuth, an hashed value integrity verification mechanism.
	
	--- Migrations.sol: This is a separate Solidity file that manages and updates the status of your deployed smart contract. This file comes with every Truffle project, and is usually not edited.
	
* migrations:

	--- 1_initial_migration.js: This file is the migration (deployment) script for the Migrations contract found in the Migrations.sol file.
	
	--- 2_deploy_contracts.js: This file is the migration (deployment) script for deploying our developed smart contract Solidity files.
	
## src
The BlendSPS prototype impelmentation by using python. 
* Client_test.py: This module provide client API functions and test cases that perform expected service operations.

* service_utils.py: This module provide test API functions to communicate with RestFul RPC exposed by microservice node.

* Tender_RPC.py: This module provide RestFul RPC functions to interact with Tendermint client.

* wrapper_pyca.py: This module provide wrapper of pyca lib for our application.

* utilities.py: This module provide utility functions to support project.

* addr_list.json: This json file records all participants' account address used in prototype.

* services_list.json: This json file saves deployed micorservice nodes' IP address used in prototype.

## test_results
The experimental results log and performance evaluation and visualization tool.
* Performance_Test.py: This module provide API functions to support data processing and results visualization.

