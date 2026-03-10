require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config({ path: "../.env" }); // reads the backend .env

const SEPOLIA_RPC_URL = process.env.ETH_RPC_URL || "";
const PRIVATE_KEY = process.env.WALLET_PRIVATE_KEY || "0x0000000000000000000000000000000000000000000000000000000000000001";

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
    solidity: {
        version: "0.8.20",
        settings: {
            optimizer: {
                enabled: true,
                runs: 200,
            },
        },
    },
    networks: {
        sepolia: {
            url: SEPOLIA_RPC_URL,
            accounts: PRIVATE_KEY !== "0x0000000000000000000000000000000000000000000000000000000000000001"
                ? [PRIVATE_KEY.startsWith("0x") ? PRIVATE_KEY : `0x${PRIVATE_KEY}`]
                : [],
            chainId: 11155111,
        },
        localhost: {
            url: "http://127.0.0.1:8545",
            chainId: 31337,
        },
    },
    etherscan: {
        // Optional: verify contract on Etherscan after deployment
        // apiKey: process.env.ETHERSCAN_API_KEY,
    },
    paths: {
        sources: "./",       // .sol files live in this (contracts/) directory
        artifacts: "./artifacts",
        cache: "./cache",
    },
};
