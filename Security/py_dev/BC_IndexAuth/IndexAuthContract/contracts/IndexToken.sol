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

	// event handle function
	event OnValueChanged(address indexed _from, uint _value);

	/* 
		function: query token data given index string and return hash data
	*/
	function getIndexToken(string str_index) public constant returns (uint, string) {

			return(indextokens[str_index].id,
					indextokens[str_index].HashValue );
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

	// Set accessright call function
	function setIndexToken(	address recipient, 
							string str_index,
							string hashed_index) public returns (bool) {
		if( supervisor == msg.sender) {
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
