pragma solidity ^0.4.18;

contract SrvExchange {

	/*
		Define struct to represent service publisher.
	*/
	struct SrvPublisher {
		uint uid;				// auto incremental number.
		address vid;			// publisher's Virtual ID, we use account address.
		string zid;				// publisher's Zone-ID, we use intra-ledger network id
		uint status;			// process status: 0-Delegation; 1-Configuration; 2-Commitment; 3-Payment
		uint balance;			// publisher's security balance to support token or currency transfer.
		string txs;			// seller's transactions list that records tx_ref of each tx. 
	}

	/*
		Define struct to represent service subscriber.
	*/
	struct SrvSubscriber {
		uint uid;				// auto incremental number.
		address vid;			// subscriber's Virtual ID, we use account address.
		string zid;				// subscriber's Zone-ID, we use intra-ledger network id
		uint status;			// process status: 0-Delegation; 1-Configuration; 2-Commitment; 3-Payment
		uint balance;			// subscriber's security balance to support token or currency transfer.
		string txs;			// buyer's transactions listthat records tx_ref of each tx.
	}


	// Global state variables
	address private constant supervisor = 0x0217f674800617172170f8e09c008b5913b9bccc;
	
	// initialize struct object 
	SrvPublisher private publisher;
	SrvSubscriber private subscriber;

	//====================================== service exchange procedures =========================================
	
	/* 
		function: query registered Publisher information
	*/
	function getPublisher() public constant returns (	address publisher_vid, 
														string publisher_zid, 
														uint publisher_status,
														uint publisher_balance, 
														string publisher_txs ) 
													{			

			publisher_vid = publisher.vid;
			publisher_zid = publisher.zid; 
			publisher_status = publisher.status;
			publisher_balance = publisher.balance;
			publisher_txs = publisher.txs;
	}

	/* 
		function: query registered Subscriber information
	*/
	function getSubscriber() public constant returns (	address subscriber_vid, 
														string subscriber_zid, 
														uint subscriber_status,
														uint subscriber_balance, 
														string subscriber_txs ) 
													{			

			subscriber_vid = subscriber.vid;
			subscriber_zid = subscriber.zid; 
			subscriber_status = subscriber.status;
			subscriber_balance = subscriber.balance;
			subscriber_txs = subscriber.txs;
	}

	/* 
		function: initialize broker info, reset all data of Publisher and Subscriber
	*/
	function initBroker() public payable returns (bool) {
		if( supervisor == msg.sender) {

			// initialize publisher
			publisher.uid = 1;
			publisher.vid = address(0);
			publisher.zid = '';
			publisher.status = 0;
			publisher.balance = 0;
			publisher.txs = '';

			// initialize subscriber
			subscriber.uid = 1;
			subscriber.vid = address(0);
			subscriber.zid = '';
			subscriber.status = 0;
			subscriber.balance = 0;
			subscriber.txs = '';

			return true;
		}
		return false;
	}

	/*
	Function: Set publisher info given delegation request [vid, zid, txs].
	*/
	function setPublisher(address addr_node, string zone_id, string txs) public returns (bool) {
		if( publisher.status == 0) {

			// update publisher data
			publisher.uid += 1;
			publisher.vid = addr_node;
			publisher.zid = zone_id;
			publisher.balance = 0;
			publisher.txs = txs;

			// set publisher as Configuration status
			publisher.status = 1;

			return true;
		}
		return false;
	}

	/*
	Function: Set subscriber info given delegation request [vid, zid, txs].
	*/
	function setSubscriber(address addr_node, string zone_id, string txs) public returns (bool) {
		if( subscriber.status == 0) {

			// update subscriber data
			subscriber.uid += 1;
			subscriber.vid = addr_node;
			subscriber.zid = zone_id;
			subscriber.balance = 0;
			subscriber.txs = txs;

			// set subscriber as Configuration status
			subscriber.status = 1;

			return true;
		}
		return false;
	}

	/*
	Function: Update publisher info given [vid, zid]. 
				This is used for broker change to handle crash faults
	*/
	function updatePublisher(address addr_node, string zone_id) public returns (bool) {
		if(supervisor == msg.sender) {

			// update publisher info
			publisher.uid += 1;
			publisher.vid = addr_node;
			publisher.zid = zone_id;

			return true;
		}
		return false;
	}

	/*
	Function: Update subscriber info given [vid, zid]. 
				This is used for broker change to handle crash faults
	*/
	function updateSubscriber(address addr_node, string zone_id) public returns (bool) {
		if(supervisor == msg.sender) {

			// update publisher info
			subscriber.uid += 1;
			subscriber.vid = addr_node;
			subscriber.zid = zone_id;

			return true;
		}
		return false;
	}		

	/*
	Function: set publisher as committed.
	*/
	function publisher_commit() public returns (bool) {
		//check if node is valid provider and current state is Registered
		if( (publisher.vid == msg.sender) && (publisher.status == 1) ) {

			// set publisher as Commitment
			publisher.uid += 1;
			publisher.status = 2;

			return true;
		}
		return false;
	}	

	/*
	Function: set subscriber as committed.
				deposit_balance: is calculated from txs by buyer
	*/
	function subscriber_commit(uint deposit_balance) public returns (bool) {
		//check if node is valid provider and current state is Registered
		if( (subscriber.vid == msg.sender) && (subscriber.status == 1) ) {
			// deposit token or currency to security balance
			subscriber.balance = deposit_balance;

			// set subscriber as Commitment
			subscriber.uid += 1;
			subscriber.status = 2;

			return true;
		}
		return false;
	}

	/*
	Function: service payment to transfer balance and re-initialize state.
	*/
	function service_payment() public returns (bool) {
		//check if both publisher and subscriber are Commitment
		if( (publisher.status == 2) && (subscriber.status == 2) ) {

			if( (publisher.vid == msg.sender) || (subscriber.vid == msg.sender) ) {
				// ---------- transfer balance -----------------
				// 1) add balance to publisher's account
				publisher.uid += 1;
				publisher.balance = subscriber.balance;
				publisher.status = 3;

				// 2) substract balance from subscriber's account
				subscriber.uid += 1;
				subscriber.balance = 0;
				subscriber.status = 3;

				return true;
			}

		}
		return false;
	}	

}
