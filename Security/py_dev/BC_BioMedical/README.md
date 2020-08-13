# BC_BioMedical
Official implementation of of paper "Decentralized autonomous imaging data processing using blockchain".
Please refer to online [link](https://www.spiedigitallibrary.org/conference-proceedings-of-spie/10871/108710U/Decentralized-autonomous-imaging-data-processing-using-blockchain/10.1117/12.2513243.short?SSO=1) for detail.

The concept proof system is deployed on a private Ethereum network. For Ethereum project, please refer to: [ethereum](https://github.com/ethereum) on github.

The overview of organization of project are:

## Contracts
The truffle project folder to develop smart contracts for identity authentication and access control on blockchain.

* contract:

	--- PatientACToken.sol: smart contract for Capability Access Control for patient data accessing mechanism.

	--- SummaryToken.sol: smart contract for Summary Data, an ideitity associated with PatientACToken.

	--- RegisterToken.sol: smart contract for Registeration: an ideitity management mechanism.
	
	--- Migrations.sol: This is a separate Solidity file that manages and updates the status of your deployed smart contract. This file comes with every Truffle project, and is usually not edited.
	
* migrations:

	--- 1_initial_migration.js: This file is the migration (deployment) script for the Migrations contract found in the Migrations.sol file.
	
	--- 2_deploy_contracts.js: This file is the migration (deployment) script for deploying our developed smart contract Solidity files.
	
* test:

	--- addr_list.json: This file provide nodename->address mapping table to manage our test nodes in private blockchain network.
	
	--- utilities.js: This javascripts offers all utility class for test code.
	
	--- test_token.js: This is a javascripts test file to interact with deployed smart contracts.
	
## src
The prototype desgin of BC_BioMedical for healthcare system by using python. 

* WS_Client.py: This module provide encapsulation of client API that access to Web service.

* WS_Server.py: This module provide encapsulation of server API that handle and response client's request.

* Test_Performance.py: This module provide performance evaluation functions given result data.

* RegisterToken.py: This module provide encapsulation of web3.py API to interact with exposed ABI of RegisterToken.sol.

* SummaryToken.py: This module provide encapsulation of web3.py API to interact with exposed ABI of SummaryToken.sol.

* PatientACToken.py: This module provide encapsulation of web3.py API to interact with exposed ABI of PatientACToken.sol.

* BlendCapAC_Policy.py: This module provide functions and encapsulation of access control policy.

* wrapper_pyca.py: This module provide wrapper of pyca lib for our application.

* utilities.py: This module provide utility functions to support project.