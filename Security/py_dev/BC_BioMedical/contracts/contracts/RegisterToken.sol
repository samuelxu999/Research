pragma solidity ^0.4.18;

contract RegisterToken {

	/*
		Define struct to represent register information.
	*/
	struct RegisterNode {
		uint uid;				// auto incremental number.
		string userID;			// user id
		address summaryToken;   // summary token address
	}


	// Global state variables
	address private constant supervisor = 0x3d40fad73c91aed74ffbc1f09f4cde7cce533671;	
	
	mapping(address => RegisterNode) UserInfo;			// associate with unique address with user data

	

	// event handle function
	event OnValueChanged(address indexed _from, uint _value);


	/* 
		function: query RegisterNode given address
	*/
	function getUserInfo(address addr_node) public constant returns (string, address) {
			return(UserInfo[addr_node].userID, UserInfo[addr_node].summaryToken);
	}


	/*
	Function: Set RegisterNode.
	*/	
	function setUserInfo(address addr_node, string user_id, address addr_summary)  public returns (bool) {
		if( supervisor == msg.sender) {
			UserInfo[addr_node].userID = user_id;
			UserInfo[addr_node].summaryToken = addr_summary;	
			return true;
		}
		else {
			return false;
		}

	}

	/*
	Function: clear RegisterNode.
	*/	
	function clearUserInfo( address addr_node )  public returns (bool) {
		if( supervisor == msg.sender) {
			UserInfo[addr_node].userID = '';
			UserInfo[addr_node].summaryToken = address(0);	
			return true;
		}
		else {
			return false;
		}

	}

}
