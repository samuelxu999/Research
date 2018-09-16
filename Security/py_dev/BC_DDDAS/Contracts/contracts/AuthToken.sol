pragma solidity ^0.4.18;

contract AuthToken {

	/*
		Define struct to represent virtual trust zone data.
	*/
	struct VTrustZone {
		uint uid;				// auto incremental number.
		address master;			// domain master address
	}

	/*
		Define struct to represent node data: master or follewers.
	*/
	struct Node {
		uint node_type;				// 0: undefined; 1: master;  2: follower.
		string VZoneID;			// Joined virtual trust zone. each node is allowed to join multiple Voznes
	}


	// Global state variables
	address private constant supervisor = 0x3d40fad73c91aed74ffbc1f09f4cde7cce533671;
	address[5] validMaster;					// used for managing valid master, maximum is 5
	uint private constant MAX_MASTERS = 5;
	//uint private constant MAX_ZONES = 3;	// maximum zones that are allowed to join for each node.
	mapping(string => VTrustZone) Vzone;	// associate with unique Vzone_ID with each Vzone data
	mapping(address => Node) Vnode;			// associate with unique address with node data

	

	// event handle function
	event OnValueChanged(address indexed _from, uint _value);

	/* 
		function: check whether master is authorized by supervisor
	*/
	function isValidMaster(address addr_master) private constant returns (bool) {
		for(uint i = 0; i < MAX_MASTERS; i++) { 
				if(validMaster[i] == addr_master) {
					return true;
				}
			}	
		return false;
	}

	/* 
		function: query valid master list from validMaster
	*/
	function getValidMaster() public constant returns (address[5]) {

			return(validMaster);
	}

	/* 
		function: query zone data given unique Vzone_ID
	*/
	function getVTrustZone(string Vzone_ID) public constant returns (address) {

			return(Vzone[Vzone_ID].master);
	}

	/* 
		function: query Vnode data given address
	*/
	function getNode(address addr_node) public constant returns (uint, string) {
			return(Vnode[addr_node].node_type, Vnode[addr_node].VZoneID);
	}


	/*
	Function: Initilized zone data given address.
	*/
	function initVTrustZone(string Vzone_ID) public returns (bool) {
		if( supervisor == msg.sender) {
			// get master of Vzone
			address Vzone_master = Vzone[Vzone_ID].master;

			// initialize Vzone_master node data
			Vnode[Vzone_master].node_type = 0;
			Vnode[Vzone_master].VZoneID = '';

			// initialize Vzone data
			Vzone[Vzone_ID].uid =0;
			Vzone[Vzone_ID].master = address(0);

			// initialize all elements in validMaster as address(0)
			for(uint i = 0; i < MAX_MASTERS; i++) { 
				if(validMaster[i] == Vzone_master) {
					validMaster[i] = address(0);
					break;
				}				
			}

			// notify OnValueChanged event
			//OnValueChanged(recipient, indextokens[str_index].id);	
			return true;

		}
		else {
			return false;
		}
	}


	/*
	Function: Add master node, which is only allowed for supervisor.
	*/	
	function addMasterNode(address addr_master)  public returns (bool) {
		if( supervisor == msg.sender) {
			// check whether master has been authorized, avoid duplicated masters
			if(isValidMaster(addr_master) == true) {
				return false; 
			}	
			// for each node in validMaster to find empty slot to add master
			for(uint i = 0; i < MAX_MASTERS; i++) { 
				// check if node[i] is empty
				if(validMaster[i] != address(0)) {
					//find next valid one
					continue;
				}
				else {
					// add addr_master to empty slot
					validMaster[i] = addr_master;
					return true;
				}
			}
			// no empty slot for add master, return false
			return false;		
		}
		else {
			return false;
		}

	}

	/*
	Function: Remove master node from validMaster.
	*/	
	function removeMasterNode(address addr_master)  public returns (bool) {
		if(supervisor == msg.sender) {

			// get Vzone_ID that is associated with master 
			string VZone_ID = Vnode[addr_master].VZoneID;

			// clear Vzone_master node data
			Vnode[addr_master].node_type = 0;
			Vnode[addr_master].VZoneID = '';

			// clear Vzone data
			Vzone[VZone_ID].uid += 1;
			Vzone[VZone_ID].master = address(0);

			// remove master from validMaster
			for(uint i = 0; i < MAX_MASTERS; i++) { 
				if(validMaster[i] == addr_master) {
					validMaster[i] = address(0);
					break;
				}				
			}
			return true;
		}
		else {
			return false;
		}	
	}

	/*
	Function: Create zone data given Vzone_ID.
	*/
	function createVZone(string Vzone_ID) public returns (bool) {
		// only allow for supervisor or valid master
		if((supervisor == msg.sender) || (isValidMaster(msg.sender) == true)) {
			// check whether virtual zone has been created by master
			if(Vzone[Vzone_ID].master == address(0)) {
				// set Vzone data by associating master with Vzone_ID
				Vzone[Vzone_ID].uid += 1;
				Vzone[Vzone_ID].master = msg.sender;

				// set Vzone_master node data
				Vnode[msg.sender].node_type = 1;
				Vnode[msg.sender].VZoneID = Vzone_ID;

				return true;
			}

			return false;
		}
		else {
			return false;
		}
	}

	/*
	Function: change master of Vzone data given Vzone_ID.
	*/
	function changeVZoneMaster(string Vzone_ID, address addr_master) public returns (bool) {
		// only allow for supervisor, and Vzone has created.
		if( (supervisor == msg.sender) && (Vzone[Vzone_ID].master != address(0)) ) {
			
			// get current master
			address curr_master = Vzone[Vzone_ID].master;

			// clear current Vzone_master node data
			Vnode[curr_master].node_type = 0;
			Vnode[curr_master].VZoneID = '';

			// set new Vzone_master node data
			Vnode[addr_master].node_type = 1;
			Vnode[addr_master].VZoneID = Vzone_ID;

			// change master in Vzone data
			Vzone[Vzone_ID].uid += 1;
			Vzone[Vzone_ID].master = addr_master;

			return true;
		}
		else {
			return false;
		}
	}

	/*
	Function: Clear zone data given Vzone_ID.
	*/
	function removeVZone(string Vzone_ID) public returns (bool) {
		// only allow for supervisor or valid master who creates the virtual zone
		if((supervisor == msg.sender) || 
			((isValidMaster(msg.sender) == true)) && (Vzone[Vzone_ID].master == msg.sender)) {

				// get current master
				address curr_master = Vzone[Vzone_ID].master;	

				// clear Vzone data
				Vzone[Vzone_ID].uid += 1;
				Vzone[Vzone_ID].master = address(0);

				// clear current Vzone_master node data
				Vnode[curr_master].node_type = 0;
				Vnode[curr_master].VZoneID = '';

				return true;
		}
		else {
			return false;
		}
	}

	/*
	Function: join virtual zone by assigning Vzone_ID to follower address.
	*/
	function joinVZone(string Vzone_ID, address node_addr) public returns (bool) {
		// only allow for supervisor or master who creates Vzone
		if((supervisor == msg.sender) || (Vzone[Vzone_ID].master == msg.sender)) {

				// set follower node data
				Vnode[node_addr].node_type = 2;
				Vnode[node_addr].VZoneID = Vzone_ID;

				return true;

		}
		else {
			return false;
		}
	}

	/*
	Function: leave virtual zone by clear follower node data.
	*/
	function leaveVZone(string Vzone_ID, address node_addr) public returns (bool) {
		// only allow for supervisor or master who creates Vzone
		if((supervisor == msg.sender) || (Vzone[Vzone_ID].master == msg.sender)) {

				// clear follower node data
				Vnode[node_addr].node_type = 0;
				Vnode[node_addr].VZoneID = '';

				return true;

		}
		else {
			return false;
		}
	}

}
