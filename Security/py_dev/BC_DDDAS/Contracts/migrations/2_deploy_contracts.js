var AuthToken = artifacts.require("./AuthToken.sol");
var CapACToken = artifacts.require("./CapACToken.sol");

module.exports = function(deployer) {
	//deployer.deploy(AuthToken);
	deployer.deploy(CapACToken);
};
