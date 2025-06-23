"""Blockchain Client for Certificate Management

Logic:
logic Web3 (kết nối, tính hash, tạo chữ ký, gửi giao dịch).
Khởi tạo hợp đồng và cung cấp các hàm gọi smart contract.
"""

import json
from web3 import Web3
from loguru import logger
from eth_account import Account
from eth_account.messages import encode_defunct
from fastapi import HTTPException

from backend.config.setting import web3_config, abi_config


class BlockchainClient:
    def __init__(self):
        """
        Khởi tạo client blockchain với Web3.
        """
        self.w3 = Web3(Web3.HTTPProvider(web3_config.infura_url))
        if not self.w3.is_connected():
            logger.error("Cannot connect to Sepolia")
            raise Exception("Cannot connect to Sepolia")

        with open(abi_config.contract_abi_path, 'r') as f:
            contract_abi = json.load(f)

        self.contract = self.w3.eth.contract(
            address=web3_config.contract_address, abi=contract_abi
        )
        self.admin_account = Account.from_key(web3_config.private_key)
        self.admin_address = self.admin_account.address
        logger.info(f"Initialize blockchain client with admin: {self.admin_address}")

    def calculate_hash(self, data: str) -> str:
        """
        Calculate hash keccak256.

        Args:
            data (str): hashing data.

        Returns:
            str: Hash data with hex.
        """
        return self.w3.keccak(text=data).hex()

    def create_signature(self, id: str, recipient_hash: str, course_hash: str) -> str:
        """
        Generate digital signature for certificate data.

        Args:
            id (str): certificate ID.
            recipient_hash (str): Hash of recipient.
            course_hash (str): Hash of course.

        Returns:
            str: hex signature.
        """
        try:
            message = self.w3.solidity_keccak(
                ['string', 'bytes32', 'bytes32'],
                [id, self.w3.to_bytes(hexstr=recipient_hash), self.w3.to_bytes(hexstr=course_hash)]
            )
            signable_message = encode_defunct(message)
            signed_message = Account.sign_message(signable_message, web3_config.private_key)
            logger.debug(f"Tạo chữ ký cho chứng chỉ ID: {id}")
            return signed_message.signature.hex()
        except Exception as e:
            logger.error(f"Lỗi khi tạo chữ ký: {str(e)}")
            raise

    async def send_transaction(self, function_call):
        """
        Transaction send to blockchain.

        Args:
            function_call: Hàm smart contract cần gọi.

        Returns:
            dict: Biên nhận giao dịch.
        """
        try:
            txn = function_call.build_transaction({
                'from': self.admin_address,
                'nonce': self.w3.eth.get_transaction_count(self.admin_address),
                'gas': 2000000,
                'gasPrice': self.w3.eth.gas_price,
            })
            signed_txn = self.w3.eth.account.sign_transaction(txn, web3_config.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            logger.info(f"Transaction successful: {tx_receipt['transactionHash'].hex()}")
            return tx_receipt
        except Exception as e:
            logger.error(f"Lỗi gửi giao dịch: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def issue_certificate(self, id: str, recipient_hash: str, course_hash: str, signature: str):
        """
        Gọi hàm issueCertificate trên smart contract.

        Args:
            id (str): certificate ID.
            recipient_hash (str): Hash of recipient.
            course_hash (str): Hash of course.
            signature (str): Digital signature.

        Returns:
            dict: Biên nhận giao dịch.
        """
        function_call = self.contract.functions.issueCertificate(
            id, self.w3.to_bytes(hexstr=recipient_hash), self.w3.to_bytes(hexstr=course_hash), self.w3.to_bytes(hexstr=signature)
        )
        return await self.send_transaction(function_call)

    async def revoke_certificate(self, id: str):
        """
        Gọi hàm revokeCertificate trên smart contract.

        Args:
            id (str): certificate ID.

        Returns:
            dict: Biên nhận giao dịch.
        """
        function_call = self.contract.functions.revokeCertificate(id)
        return await self.send_transaction(function_call)

    def verify_certificate(self, id: str):
        """
        Gọi hàm verifyCertificate trên smart contract.

        Args:
            id (str): certificate ID.

        Returns:
            tuple: Dữ liệu chứng chỉ (id, recipientHash, courseHash, issueDate, signature).
        """
        try:
            cert = self.contract.functions.verifyCertificate(id).call()
            logger.debug(f"Tra cứu chứng chỉ ID: {id}")
            return cert
        except Exception as e:
            logger.error(f"Lỗi tra cứu chứng chỉ: {str(e)}")
            raise HTTPException(status_code=404, detail=str(e))