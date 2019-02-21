pragma solidity ^0.4.18;

contract SummaryToken {

	/*
		Define struct to represent summary toekn.
	*/
	struct SummaryNode {
		uint uid;				// auto incremental number.
		address[5] patientACToken;   // PatientACToken address
	}


	// Global state variables
	address private constant supervisor = 0x3d40fad73c91aed74ffbc1f09f4cde7cce533671;

	mapping(address => SummaryNode) SummaryInfo;	// associate with unique address with SummaryNode data

	uint private constant MAX_PatientACToken = 5;
	

	// event handle function
	event OnValueChanged(address indexed _from, uint _value);

	/* 
		function: query SummaryNode given address
	*/
	function getSummaryInfo(address addr_node) public constant returns (address[5]) {
			return(SummaryInfo[addr_node].patientACToken);
	}


	/* 
		function: add PatientACToken given user address
	*/
	function addPatientACToken(address patient, address patientACToken) public returns (bool) {
		bool ret = false;

		if( (supervisor == msg.sender) || (patient==msg.sender) ) {
			uint free_index = 0;
			bool isExist = false;
			for(free_index = 0; free_index < MAX_PatientACToken; free_index++) {
				//check if the patientACToken address is already exist
				if(SummaryInfo[patient].patientACToken[free_index] == patientACToken) {
					isExist = true;
					break;
				}
			}

			// no duplicate address
			if(isExist == false) {
				for(free_index = 0; free_index < MAX_PatientACToken; free_index++) {
					//check if the address is not used
					if(SummaryInfo[patient].patientACToken[free_index] == address(0)) {
						break;
					}
				}
				if(free_index < MAX_PatientACToken) {
					SummaryInfo[patient].uid += 1;
					SummaryInfo[patient].patientACToken[free_index] = patientACToken;
					OnValueChanged(patient, SummaryInfo[patient].uid);
					ret = true;
				}
			}
		}
		return ret;	
	}


	/* 
		function: remove PatientACToken given user address
	*/
	function removePatientACToken(address patient, address patientACToken) public returns (bool) {
		bool ret = false;

		if( (supervisor == msg.sender) || (patient==msg.sender) ) {
			uint free_index = 0;
			for(free_index = 0; free_index < MAX_PatientACToken; free_index++) {
				//check if the address is exist
				if(SummaryInfo[patient].patientACToken[free_index] == patientACToken) {
					break;
				}
			}
			if(free_index < MAX_PatientACToken) {
				SummaryInfo[patient].uid += 1;
				SummaryInfo[patient].patientACToken[free_index] = address(0);
				OnValueChanged(patient, SummaryInfo[patient].uid);
				ret = true;
			}

		}
		return ret;	
	}
	
}
