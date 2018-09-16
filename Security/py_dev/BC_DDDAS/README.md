# BC_DDDAS
Official implementation of the "An Exploration of Blockchain Enabled Decentralized Capability based Access Control Strategy for Space Situation Awareness"

The concept proof system is deployed on a private Ethereum network. For Ethereum project, please refer to: [ethereum](https://github.com/ethereum) on github.

The overview of organization of project are:

## Contracts
The truffle project folder to develop smart contracts for identity authentication and access control on blockchain.

* contract:

	--- AuthToken.sol: smart contract for proof concept demo: Virtual Trust Zone, an ideitity authentication mechanism.
	
	--- Migrations.sol: This is a separate Solidity file that manages and updates the status of your deployed smart contract. This file comes with every Truffle project, and is usually not edited.
	
* migrations:

	--- 1_initial_migration.js: This file is the migration (deployment) script for the Migrations contract found in the Migrations.sol file.
	
	--- 2_deploy_contracts.js: This file is the migration (deployment) script for deploying our developed smart contract Solidity files.
	
* test:

	--- addr_list.json: This file provide nodename->address mapping table to manage our test nodes in private blockchain network.
	
	--- utilities.js: This javascripts offers all utility class for test code.
	
	--- test_token.js: This is a javascripts test file to interact with deployed smart contracts.
	
## src
The prototype desgin of Index authentication for smart surveillance system by using python. 
* WS_Client.py: This module provide encapsulation of client API that access to Web service.

* WS_Server.py: This module provide encapsulation of server API that handle and response client's request.

* AuthToken.py: This module provide encapsulation of web3.py API to interact with exposed ABI of AuthToken.sol.

* Auth_Policy.py: This module provide functions and encapsulation of index authentication policy.

* wrapper_pyca.py: This module provide wrapper of pyca lib for our application.

* utilities.py: This module provide utility functions to support project.