// scripts/deploy.js
// Deploys the EnvironmentalCredit contract to the selected network.
//
// Usage:
//   cd backend/contracts
//   npm install
//   npx hardhat run scripts/deploy.js --network sepolia
//
// After deployment, copy the printed CONTRACT_ADDRESS into your backend/.env

const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
    console.log("🚀 Deploying EnvironmentalCredit...");
    console.log("   Network:", hre.network.name);

    const [deployer] = await hre.ethers.getSigners();
    console.log("   Deployer:", deployer.address);

    const balance = await hre.ethers.provider.getBalance(deployer.address);
    console.log("   Balance :", hre.ethers.formatEther(balance), "ETH");

    const Factory = await hre.ethers.getContractFactory("EnvironmentalCredit");
    const contract = await Factory.deploy();
    await contract.waitForDeployment();

    const address = await contract.getAddress();
    console.log("\n✅  EnvironmentalCredit deployed to:", address);
    console.log("   Add this to backend/.env:");
    console.log(`   CONTRACT_ADDRESS=${address}`);

    // -----------------------------------------------------------------------
    // Export ABI for the Flask backend
    // -----------------------------------------------------------------------
    const artifact = await hre.artifacts.readArtifact("EnvironmentalCredit");
    const abiPath = path.join(__dirname, "..", "EnvironmentalCredit_abi.json");
    fs.writeFileSync(abiPath, JSON.stringify(artifact.abi, null, 2));
    console.log(`\n📄  ABI written to ${abiPath}`);
    console.log("   The Flask backend will load it automatically.");
}

main().catch((err) => {
    console.error(err);
    process.exitCode = 1;
});
