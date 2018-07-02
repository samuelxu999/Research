/*
=========================== This is demo test script to acces our smart token object =======================================
*/

// Interaction with Ethereum
var Web3 = require('web3');
const myUtility = require('./utilities');
var web3 = new Web3();

// connect to the local node
web3.setProvider(new web3.providers.HttpProvider('http://localhost:8042'));

// The contract address that we are going to interact with
var contractAddress = '0xb71e920f014cddc0064ed166e10a0126ef76f537';

// Load node addresses data from SmartToken.json
var config = require('../build/contracts/IndexToken.json');

// Read ABI(Application Binary Interface)
var ABI = config.abi;

// new contract object according to ABI and address
var contract = web3.eth.contract(ABI).at(contractAddress);

//-------------------------- test demo -------------------------------
str_index = '1';

//read token data before transaction
get_token(str_index);


// set token test
//setToken_test();

//bind event onChange
account_onValueChanged(str_index);


//====================================== function for test ==================================
// wait for an event triggered on the Smart Contract
function account_onValueChanged(str_index) {
	var onValueChanged = contract.OnValueChanged({_from: web3.eth.coinbase});

	//open watching.
	onValueChanged.watch(function(error, result) {
		if (!error) {
			// get token status
			var tokenData = contract.getIndexToken(str_index);
			console.log(tokenData);

			//stop watching
			onValueChanged.stopWatching();
		}
	})
}

function get_token(str_index) {

	// get token status
	var tokenData = contract.getIndexToken(str_index);

	for (var i = 0; i <tokenData.length; i++) {
		console.log(tokenData[i]);
	}
}

// launch depositToken transaction
function setToken_test() {
	var ret = 0;
	// initialize token
	//ret=contract.initIndexToken( web3.eth.coinbase, '1', {from: web3.eth.coinbase} );

	// change hashed value in token
	ret=contract.setIndexToken(web3.eth.coinbase, '1', 'samuel', {from: web3.eth.coinbase});

	console.log(ret);
}

//get address from json file
function getAddress(node_name){
	// Load config data from SmartToken.json
	var addrlist = require('./addr_list.json');	
	return addrlist[node_name];	
}


