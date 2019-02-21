pragma solidity ^0.4.18;

contract PatientACToken {

	/*
		Define struct to represent capability token data.
	*/
	struct CapabilityToken {
		uint id;				// token id
		bool initialized;		//check whether token has been initialized
		bool isValid;			// flage to indicate whether token valid, used for temporary dispense operation
		uint256 issuedate;		// token issued date
		uint256 expireddate;	// token expired date
		string authorization;
	}

	// --------------------------------- Global state variables -------------------------
	address private constant supervisor = 0x3d40fad73c91aed74ffbc1f09f4cde7cce533671;
	address private VZone_master = address(0);
	mapping(address => CapabilityToken) captokens;

	// event handle function
	event OnValueChanged(address indexed _from, uint _value);

	/* 
		function: query token data given address and return general token data
	*/
	function getCapTokenStatus(address addr_node) public constant returns (uint, 
																			address,
																			bool, 
																			bool, 
																			uint256, 
																			uint256,
																			string) {

			return(	captokens[addr_node].id, 
					VZone_master,
					captokens[addr_node].initialized,
					captokens[addr_node].isValid,
					captokens[addr_node].issuedate,
					captokens[addr_node].expireddate,
					captokens[addr_node].authorization
					);
	}

	/*
	Function: set VZone master to mamage token.
	*/
	function assignVZoneMaster(address addr_master) public returns (bool) {
		// only allow for supervisor
		if( supervisor == msg.sender) {
			//set default access right
			VZone_master = addr_master;	

			return true;

		}
		else {
			return false;
		}
	}

	/*
	Function: set VZone master to mamage token .
	*/
	function revokeVZoneMaster() public returns (bool) {
		// only allow for supervisor
		if( supervisor == msg.sender) {
			//set default access right
			VZone_master = address(0);	

			return true;

		}
		else {
			return false;
		}
	}


	/*
	Function: Initilized token data given address.
	*/
	function initCapToken(address addr_node) public returns (bool) {
		// only allow for supervisor or domain master
		if( (supervisor == msg.sender) ||( VZone_master == msg.sender )) {
			//set id and initialized flag
			captokens[addr_node].id = 1;
			captokens[addr_node].initialized = true;

			//disable token
			captokens[addr_node].isValid = false;

			//captokens[addr_node].issuedate = now;
			//captokens[addr_node].expireddate = now + 1 days;

			//set default access right
			captokens[addr_node].authorization = "";	

			// notify OnValueChanged event
			OnValueChanged(addr_node, captokens[addr_node].id);	
			return true;

		}
		else {
			return false;
		}
	}

	// Set isValid flag call function
	function setCapToken_isValid(address addr_node, bool isValid) public returns (bool) {
		// only allow for supervisor or domain master
		if( (supervisor == msg.sender) || (VZone_master == msg.sender) || (addr_node == msg.sender) ) {
			captokens[addr_node].id += 1;
			captokens[addr_node].isValid = isValid;
			OnValueChanged(addr_node, captokens[addr_node].id);
			return true;
		}
		else{
			return false;
		}
		
	}

	// Set time limitation call function
	function setCapToken_expireddate(address addr_node, 
									uint256 issueddate, 
									uint256 expireddate) public returns (bool) {
		// only allow for supervisor or domain master
		if( (supervisor == msg.sender) ||(VZone_master == msg.sender) || (addr_node == msg.sender) ) {
			captokens[addr_node].id += 1;
			captokens[addr_node].issuedate = issueddate;
			captokens[addr_node].expireddate = expireddate;
			OnValueChanged(addr_node, captokens[addr_node].id);
			return true;
		}
		else {
			return false;
		}
	}

	// Set accessright call function
	function setCapToken_authorization(address addr_node, 
										string accessright) public returns (bool) {
		// only allow for supervisor, domain master
		if( (supervisor == msg.sender) ||(VZone_master == msg.sender) || (addr_node == msg.sender)) {
			captokens[addr_node].id += 1;
			captokens[addr_node].authorization = accessright;
			OnValueChanged(addr_node, captokens[addr_node].id);
			return true;
		}
		else{
			return false;
		}
		
	}
}