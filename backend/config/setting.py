import os
from pydantic import Field
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Web3Config(BaseSettings):
    infura_url: str = Field(
        description="Infura URL for connecting to the Sepolia network",
        alias='INFURA_URL'
    )
    private_key: str = Field(
        description="Private key for the admin account",
        alias='PRIVATE_KEY'
    )
    contract_address: str = Field(
        description="Smart contract address on the Sepolia network",
        alias='CONTRACT_ADDRESS'
    )
    
class MongoDBConfig(BaseSettings):
    mongodb_uri: str = Field(
        description="MongoDB URI for connecting to the database",
        alias='MONGODB_URI'
    )
    db_name: str = Field(
        default='certificate_db',
        description="Name of the MongoDB database"
    )
    collection_name: str = Field(
        default='certificates',
        description="Name of the MongoDB collection for certificates"
    )
    user_collection_name: str = Field(
        default='users',
        description="Name of the MongoDB collection for user accounts"
    )
    admin_collection_name: str = Field(
        default='admins',
        description="Name of the MongoDB collection for admin accounts"
    )
    admin_log_collection_name: str = Field(
        default='admin_logs',
        description="Name of the MongoDB collection for admin logs"
    )

class ABIConfig(BaseSettings):
    contract_abi_path: str = Field(
        default='contracts/contract_abi.json',
        description="Path to the smart contract ABI file",
        alias='CONTRACT_ABI_PATH'
    )

web3_config = Web3Config()
db_config = MongoDBConfig()
abi_config = ABIConfig()