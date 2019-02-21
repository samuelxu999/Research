var RegisterToken = artifacts.require("./RegisterToken.sol");
var SummaryToken = artifacts.require("./SummaryToken.sol");
var PatientACToken = artifacts.require("./PatientACToken.sol");

module.exports = function(deployer) {
	//deployer.deploy(RegisterToken);
	//deployer.deploy(SummaryToken);
	deployer.deploy(PatientACToken);
};
