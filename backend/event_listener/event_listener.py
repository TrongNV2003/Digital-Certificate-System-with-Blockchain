import asyncio
from loguru import logger

from backend.db.connector import MongoDBClient
from backend.blockchain.blockchain import BlockchainClient


async def listen_events():
    """
    Lắng nghe các sự kiện blockchain và cập nhật MongoDB.
    """
    mongo_client = MongoDBClient()
    blockchain_client = BlockchainClient()

    event_filter = blockchain_client.contract.events.CertificateIssued.create_filter(filter_params={'fromBlock': 'latest'})
    revoke_filter = blockchain_client.contract.events.CertificateRevoked.create_filter(filter_params={'fromBlock': 'latest'})
    admin_added_filter = blockchain_client.contract.events.AdminAdded.create_filter(filter_params={'fromBlock': 'latest'})
    admin_removed_filter = blockchain_client.contract.events.AdminRemoved.create_filter(filter_params={'fromBlock': 'latest'})

    while True:
        try:
            for event in event_filter.get_new_entries():
                mongo_client.update_certificate(event['args']['id'], {
                    'event': 'CertificateIssued',
                    'recipientHash': event['args']['recipientHash'].hex(),
                    'courseHash': event['args']['courseHash'].hex(),
                    'issueDate': event['args']['issueDate'],
                    'signature': event['args']['signature'].hex()
                })
                logger.info(f"Xử lý sự kiện CertificateIssued cho ID: {event['args']['id']}")

            for event in revoke_filter.get_new_entries():
                mongo_client.update_certificate(event['args']['id'], {
                    'event': 'CertificateRevoked',
                    'revoked': True
                })
                logger.info(f"Xử lý sự kiện CertificateRevoked cho ID: {event['args']['id']}")

            for event in admin_added_filter.get_new_entries():
                mongo_client.update_admin(event['args']['admin'], 'active')
                logger.info(f"Xử lý sự kiện AdminAdded cho địa chỉ: {event['args']['admin']}")

            for event in admin_removed_filter.get_new_entries():
                mongo_client.update_admin(event['args']['admin'], 'removed')
                logger.info(f"Xử lý sự kiện AdminRemoved cho địa chỉ: {event['args']['admin']}")

        except Exception as e:
            logger.error(f"Lỗi khi xử lý sự kiện: {str(e)}")

        await asyncio.sleep(10)