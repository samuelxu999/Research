pragma solidity ^0.4.18;

contract IndexToken {

	/*
		Define struct to represent index token data.
	*/
	struct indextoken {
		uint id;					// internal id
		string HashValue;		// index hash value
	}

	// Global state variables
	address private constant supervisor = 0x3d40fad73c91aed74ffbc1f09f4cde7cce533671;
	mapping(string => indextoken) indextokens;
	address[5] authorizedNodes;		// authorized nodes to interact with ABI, maximum is 5
	uint private constant MAX_NODES = 5;

	// event handle function
	event OnValueChanged(address indexed _from, uint _value);

	/* 
		function: check whether node is authorized by supervisor
	*/
	function isAuthrozied(address recipient) private constant returns (bool) {
		for(uint i = 0; i < MAX_NODES; i++) { 
				if(authorizedNodes[i] == recipient) {
					return true;
				}
			}	
		return false;
	}

	/* 
		function: query token data given index string and return hash data
	*/
	function getIndexToken(string str_index) public constant returns (uint, string) {

			return(indextokens[str_index].id,
					indextokens[str_index].HashValue );
	}

	/* 
		function: query authorized node data
	*/
	function getAuthorizedNodes() public constant returns (address[5]) {
		address[5] emptynodes;
		if( supervisor == msg.sender) {
			return(authorizedNodes);
		}
		else {
			return(emptynodes);
		}
	}


	/*
	Function: Initilized token data given address.
	*/
	function initIndexToken(address recipient, string str_index) public returns (bool) {
		if( supervisor == msg.sender) {
			//set id as 1
			indextokens[str_index].id = 0;
			indextokens[str_index].HashValue = '';

			// notify OnValueChanged event
			OnValueChanged(recipient, indextokens[str_index].id);	
			return true;

		}
		else {
			return false;
		}
	}

	/*
	Function: Add authroized nodes.
	*/	
	function addAuthorizedNodes(address recipient)  public returns (bool) {
		if( supervisor == msg.sender) {
			// check whether node has been authorized, avlid duplicated nodes
			if(isAuthrozied(recipient) == true) {
				return false; 
			}
			// for each node to find empty slot to add recipient
			for(uint i = 0; i < MAX_NODES; i++) { 
				// check if node[i] is empty
				if(authorizedNodes[i] != address(0)) {
					//find next valid one
					continue;
				}
				else {
					// add recipient to empty slot
					authorizedNodes[i] = recipient;
					return true;
				}
			}
			// no empty slot for add recipient, return false
			return false;
		}
		else {
			return false;
		}		
	}

	/*
	Function: Remove authroized nodes.
	*/	
	function removeAuthorizedNodes(address recipient)  public returns (bool) {
		if( supervisor == msg.sender) {
			// for each node to find  recipient to remove
			for(uint i = 0; i < MAX_NODES; i++) { 
				// check if node[i] is recipient
				if(authorizedNodes[i] != recipient) {
					//find next valid one
					continue;
				}
				else {
					// remove recipient from authorizedNodes
					authorizedNodes[i] = address(0);
					return true;
				}
			}
			// no recipient for remove, return false
			return false;
		}
		else {
			return false;
		}	
	}

	// Set accessright call function
	function setIndexToken(	address recipient, 
							string str_index,
							string hashed_index) public returns (bool) {
		if( supervisor == msg.sender || isAuthrozied(recipient) == true) {
			indextokens[str_index].id += 1;
			indextokens[str_index].HashValue = hashed_index;
			OnValueChanged(recipient, indextokens[str_index].id);
			return true;
		}
		else{
			return false;
		}
		
	}
}
