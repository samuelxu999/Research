var AuthToken = artifacts.require("./AuthToken.sol");
var CapACToken = artifacts.require("./CapACToken.sol");
var IndexToken = artifacts.require("./IndexToken.sol");

module.exports = function(deployer) {
	//deployer.deploy(AuthToken);
	deployer.deploy(CapACToken);
	//deployer.deploy(IndexToken);
};
