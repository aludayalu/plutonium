const fs = require("fs")

async function main() {
    const [deployer] = await ethers.getSigners();
    console.log("Deploying contracts with the account:", deployer.address);
    const MyContract = await ethers.getContractFactory("Lock");
    const myContract = await MyContract.deploy();
    console.log("Contract deployed to:", myContract.target);
    fs.writeFileSync("../contract.hash", String(myContract.target))
}

main()
.then(() => process.exit(0))
.catch((error) => {
    console.error(error);
    process.exit(1);
});