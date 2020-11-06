# BC_BioMedical
Official implementation of of paper "Hybrid blockchain-enabled secure microservices fabric for decentralized multi-domain avionics systems".
Please refer to online [link](hhttps://doi.org/10.1117/12.2559036) for detail.

The concept proof system is deployed on a private Tendermint network. For Tendermint network setup, please refer to: [Tendermint_dev](https://github.com/samuelxu999/Blockchain_dev/tree/master/Tendermint) on github.

The overview of organization of project are:
	
## src
The prototype desgin of BC_BioMedical for healthcare system by using python. 

* RPC_Client.py: python wrapper of curl abci for interacting with tendermint network through RPC

* Client_test.py: This module provide encapsulation of client API that launch requests based different test scenarios.

* utilities.py: This module provide utility functions to support project.