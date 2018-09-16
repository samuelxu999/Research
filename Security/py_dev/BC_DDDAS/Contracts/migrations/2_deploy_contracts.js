var AuthToken = artifacts.require("./AuthToken.sol");

module.exports = function(deployer) {
	deployer.deploy(AuthToken);
};
