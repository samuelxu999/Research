pragma solidity ^0.4.18;

contract SrvExchange {

	/*
		Define struct to represent account of each participant.
	*/
	struct Account {
		uint uid;					// auto incremental number.
		uint balance;				// balance to record time currency
		uint status;				// current status: 0-Initialized; 1-active; 2-inactive
	}

	/*
		Define struct to represent dealer.
	*/
	struct SrvDealer {
		uint uid;					// auto incremental number.
		uint balance;				// balance to record time currency for payment
	}

	/*
		Define struct to represent service provider.
	*/
	struct SrvProvider {
		uint uid;					// auto incremental number.
		address VID;				// provider's VID, we use account address.
		string serviceInfo;			// service information by provider
		uint status;				// current status: 0-Initialized; 1-Registered; 2-Confirmed; 3-Committed
	}

	/*
		Define struct to represent service recipient.
	*/
	struct SrvRecipient {
		uint uid;					// auto incremental number.
		address VID;				// recipient's VID, we use account address.
		string serviceInfo;			// service information by provider
		uint status;				// current status: 0-Initialized; 1-Registered; 2-Confirmed; 3-Committed
	}


	// Global state variables
	address private constant supervisor = 0x0217f674800617172170f8e09c008b5913b9bccc;
	
	// initialize struct object 
	SrvDealer private dealer;
	SrvProvider private provider;
	SrvRecipient private recipient;

	mapping(address => Account) TB_account;			// associate with unique address with account data

	//====================================== Account procedures =========================================
	/* 
		function: query TB_account data given address
	*/
	function getAccount(address addr_node) public constant returns (uint, uint, uint) {
			return(	TB_account[addr_node].uid,
					TB_account[addr_node].balance, 
					TB_account[addr_node].status);
	}
	

	/*
	Function: Initilized TB_account data given address.
	*/
	function initAccount(address addr_node) public returns (bool) {
		if( supervisor == msg.sender) {

			// initialize Vzone_master node data
			TB_account[addr_node].uid = 0;
			TB_account[addr_node].balance = 0;
			TB_account[addr_node].status = 0;

			return true;
		}
		return false;
	}

	/*
	Function: Set TB_account status and balance given address.
	*/
	function setAccount(address addr_node, uint status, uint balance) public returns (bool) {
		if( supervisor == msg.sender) {

			// increase uid for each update
			TB_account[addr_node].uid += 1;
			// set status and balance
			TB_account[addr_node].status = status;
			TB_account[addr_node].balance = balance;

			return true;
		}
		return false;
	}

	//====================================== service exchange procedures =========================================
	
	/* 
		function: query registered service data
	*/
	function getService() public constant returns (	uint dealer_uid, 
													uint dealer_balance,
													address provider_VID, 
													string provider_serviceInfo, 
													uint provider_status,
													address recipient_VID, 
													string recipient_serviceInfo, 
													uint recipient_status) 
													{			

			dealer_uid = dealer.uid;
			dealer_balance = dealer.balance;
			provider_VID = provider.VID;
			provider_serviceInfo = provider.serviceInfo; 
			provider_status = provider.status;
			recipient_VID = recipient.VID;
			recipient_serviceInfo = recipient.serviceInfo;
			recipient_status = recipient.status;
	}

	/* 
		function: initialize service data
	*/
	function initService() public payable returns (bool) {
		if( supervisor == msg.sender) {

			// initialize dealer
			dealer.uid = 1;
			dealer.balance = 0;

			// initialize provider
			provider.uid = 1;
			provider.VID = address(0);
			provider.serviceInfo = 'empty';
			provider.status = 0;

			// initialize recipient
			recipient.uid = 1;
			recipient.VID = address(0);
			recipient.serviceInfo = 'empty';
			recipient.status = 0;

			return true;
		}
		return false;
	}

	/*
	Function: Update provider data given address.
	*/
	function updateProvider(address addr_node, string serviceInfo) public returns (bool) {
		if( provider.status == 0) {

			// update provider data
			provider.uid += 1;
			provider.VID = addr_node;
			provider.serviceInfo = serviceInfo;

			// set provider as Registered
			provider.status = 1;

			return true;
		}
		return false;
	}	

	/*
	Function: Update recipient data given address.
	*/
	function updateRecipient(address addr_node, string serviceInfo) public returns (bool) {
		if( recipient.status == 0) {

			// update recipient data
			recipient.uid += 1;
			recipient.VID = addr_node;
			recipient.serviceInfo = serviceInfo;

			// set recipient as Registered
			recipient.status = 1;

			return true;
		}
		return false;
	}	

	/*
	Function: set recipient deposit time currency into dealer balance.
	*/
	function recipient_deposit(address addr_node, uint time_currency) public returns (bool) {
		//check if node is valid recipient and current state is Registered
		if( (recipient.VID == addr_node) && (recipient.status == 1) ) {

			// update dealer data
			dealer.uid += 1;
			dealer.balance = time_currency;

			// set recipient as Confirmed
			recipient.uid += 1;
			recipient.status = 2;

			return true;
		}
		return false;
	}

	/*
	Function: remove recipient time currency from dealer balance.
	*/
	function recipient_withdraw(address addr_node) public returns (bool) {
		//check if node is valid recipient and current state is Registered
		if( (recipient.VID == addr_node) && (recipient.status == 2) ) {

			// update dealer data
			dealer.uid += 1;
			dealer.balance = 0;

			// set recipient as Registered
			recipient.uid += 1;
			recipient.status = 1;
			return true;
		}
		return false;
	}


	/*
	Function: set provider as Confirmed.
	*/
	function provider_confirm(address addr_node) public returns (bool) {
		//check if node is valid provider and current state is Registered
		if( (provider.VID == addr_node) && (provider.status == 1) ) {

			// set provider as Confirmed
			provider.uid += 1;
			provider.status = 2;

			return true;
		}
		return false;
	}	

	/*
	Function: set service Committed state given address.
	*/
	function service_commit(address addr_node) public returns (bool) {
		//check if both provider and recipient are Confirmed
		if( (provider.VID == addr_node) && (provider.status == 2) ) {
			// set provider as Committed
			provider.uid += 1;
			provider.status = 3;
			return true;
		}

		if( (recipient.VID == addr_node) && (recipient.status == 2) ) {
			// set recipient as Committed
			recipient.uid += 1;
			recipient.status = 3;
			return true;
		}
		return false;
	}	

	/*
	Function: service payment to transfer balance and re-initialize state.
	*/
	function service_payment(address addr_node) public returns (bool) {
		//check if both provider and recipient are Confirmed
		if( (provider.status == 3) && (recipient.status == 3) ) {

			if( (provider.VID == addr_node) || (recipient.VID == addr_node) ) {
				// ---------- transfer time currency -----------------
				// 1) add time to provider's account
				TB_account[provider.VID].uid += 1;
				TB_account[provider.VID].balance += dealer.balance;	
				// 2) substract time from recipient's account
				TB_account[recipient.VID].uid += 1;
				TB_account[recipient.VID].balance -= dealer.balance;					

				// reset dealer balance
				dealer.uid += 1;
				dealer.balance = 0;

				// Reset provider data
				provider.uid += 1;
				provider.VID = address(0);
				provider.serviceInfo = '';
				provider.status = 0;

				// Reset recipient data
				recipient.uid += 1;
				recipient.VID = address(0);
				recipient.serviceInfo = '';
				recipient.status = 0;

				return true;
			}

		}
		return false;
	}	

}
