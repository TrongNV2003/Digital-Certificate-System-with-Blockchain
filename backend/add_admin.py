import asyncio

from backend.blockchain.blockchain import BlockchainClient
from backend.config.setting import web3_config

async def main():
    client = BlockchainClient()
    tx = await client.add_admin(web3_config.contract_address)
    print(f"Transaction hash: {tx['transactionHash'].hex()}")

if __name__ == "__main__":
    asyncio.run(main())