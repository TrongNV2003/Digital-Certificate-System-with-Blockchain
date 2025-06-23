# Digital Issue Certificate System with Blockchain
The project deploys a digital certificate system on the Sepolia testnet, using Solidity, FastAPI, React, and MongoDB. Also using Infura, that allows the back-end (FastAPI with web3.py) connect to the Sepolia Blockchain network, to send transactions, look up data, or listen for events. Then connecting to Smart Contract via Web3.py library.

## Installation
1. Install back-end: `cd backend && pip install -r requirements.txt`
2. Install front-end: `cd frontend && npm install`
3. Configuration `.env` (watch `.env.example`)

## Instruction
- To open wallet, please install MetaMask Extensions on Chrome.
- To get ETH on testnet, you can ask ETH from [Here](https://cloud.google.com/application/web3/faucet/ethereum/sepolia) 
- Check balance account on testnet Sepolia: https://sepolia.etherscan.io/address/CONTRACT_ADDRESS
- Register Infura to connect your backend to Sepolia Blockchain network from [Here](https://www.infura.io/)

## Note
- This is a project on Sepolia testnet, not for mainnet, Only for academic and research projects.