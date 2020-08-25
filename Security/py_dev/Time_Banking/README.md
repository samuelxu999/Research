## BIT
Official implementation of paper "BIT: A Blockchain Integrated Time Banking System for Community Exchange Economy". 

For Ethereum private network configuration, please refer to [link](https://github.com/samuelxu999/Blockchain_dev/tree/master/MyChains).

For smart contract development, please refer to [Truffle](https://truffleframework.com/docs) for truffle environment setup and usage. The demo application is developed by python and Flask.

### Microservices implementation
The concept proof system is deployed and run on a microservices SOA framework. You can access microservices projects reousrce on github: 
[AuthID](https://github.com/samuelxu999/Microservices_dev/tree/master/Services_dev/AuthID); 
[BlendCAC](https://github.com/samuelxu999/Microservices_dev/tree/master/Services_dev/BlendCAC); 
[TimeBanking](https://github.com/samuelxu999/Microservices_dev/tree/master/Services_dev/TimeBanking).


### contract_dev
This is truffle folder to develop smart contract for TB service exchange implementation.
* contract:

	--- SrvExchange.sol: Service exchange contract to support service querying, negotiation and payment.
	
	--- Migrations.sol: This is a separate Solidity file that manages and updates the status of your deployed smart contract. This file comes with every Truffle project, and is usually not edited.
	
* migrations:

	--- 1_initial_migration.js: This file is the migration (deployment) script for the Migrations contract found in the Migrations.sol file.
	
	--- 2_deploy_contracts.js: This file is the migration (deployment) script for deploying our developed smart contract Solidity files.
	

### src
The prototype desgin of BIT by using python. 
* SrvExchangeToken.py: This module provide encapsulation of web3.py API to interact with SrvExchange.sol smart contract.

* SrvExchange_Server.py: This module provide encapsulation of RestFul web-service API that handle and response client's request.

* Test_Client.py: This module defines test cases to evaluate performance.

* addr_list.json: This json file records all participants' account address used in prototype.

* service_utils.py: This module provide encapsulation of TB SrvExchangeClient API that access to RestFul web-service API.

* services_list.json: This json file saves deployed micorservice nodes' IP address used in prototype.

* utilities.py: This module provide basic utility functions to support project.
