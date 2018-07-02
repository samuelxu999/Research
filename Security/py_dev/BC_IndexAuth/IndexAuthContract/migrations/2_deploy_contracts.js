var IndexToken = artifacts.require("./IndexToken.sol");

module.exports = function(deployer) {
	deployer.deploy(IndexToken);
};
