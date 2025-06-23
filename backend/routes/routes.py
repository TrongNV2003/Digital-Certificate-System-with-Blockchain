from loguru import logger
from fastapi import APIRouter, HTTPException

from backend.db.connector import MongoDBClient
from backend.blockchain.blockchain import BlockchainClient
from backend.utils.utils import CertificateInput, RevokeInput

router = APIRouter(prefix="/api", tags=["Certificate"])

mongo_client = MongoDBClient()
blockchain_client = BlockchainClient()


@router.post("/issue-certificate")
async def issue_certificate(data: CertificateInput):
    """
    Issue new certificate and save to MongoDB.

    Args:
        data (CertificateInput): Certificate data (id, recipient, course).

    Returns:
        dict: Thông báo và txHash.
    """
    try:
        recipient_hash = blockchain_client.calculate_hash(data.recipient)
        course_hash = blockchain_client.calculate_hash(data.course)
        signature = blockchain_client.create_signature(data.id, recipient_hash, course_hash)

        tx_receipt = await blockchain_client.issue_certificate(
            data.id, recipient_hash, course_hash, signature
        )

        certificate_data = {
            'id': data.id,
            'recipient': data.recipient,
            'recipientHash': recipient_hash,
            'course': data.course,
            'courseHash': course_hash,
            'issueDate': int(blockchain_client.w3.eth.get_block('latest').timestamp),
            'signature': signature,
            'txHash': tx_receipt['transactionHash'].hex(),
            'revoked': False
        }
        mongo_client.insert_certificate(certificate_data)

        return {
            'message': 'Cấp chứng chỉ thành công',
            'txHash': tx_receipt['transactionHash'].hex()
        }
    except Exception as e:
        logger.error(f"Lỗi khi cấp chứng chỉ: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/revoke-certificate")
async def revoke_certificate(data: RevokeInput):
    """
    Revoke certificate and update MongoDB.

    Args:
        data (RevokeInput): Certificate data (id).

    Returns:
        dict: Thông báo và txHash.
    """
    try:
        tx_receipt = await blockchain_client.revoke_certificate(data.id)
        mongo_client.update_certificate(data.id, {
            'revoked': True,
            'revokeTxHash': tx_receipt['transactionHash'].hex(),
            'event': 'CertificateRevoked'
        })
        return {
            'message': 'Revoke certificate successfully',
            'txHash': tx_receipt['transactionHash'].hex()
        }
    except Exception as e:
        logger.error(f"Lỗi khi thu hồi chứng chỉ: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/verify-certificate/{id}")
async def verify_certificate(id: str):
    """
    Tra cứu chứng chỉ từ blockchain và MongoDB.

    Args:
        id (str): ID chứng chỉ.

    Returns:
        dict: Thông tin chứng chỉ.
    """
    try:
        cert = blockchain_client.verify_certificate(id)
        cert_data = mongo_client.find_certificate(id)

        if not cert_data:
            raise HTTPException(status_code=404, detail="Không tìm thấy dữ liệu gốc")

        return {
            'id': cert[0],
            'recipient': cert_data['recipient'],
            'recipientHash': cert[1].hex(),
            'course': cert_data['course'],
            'courseHash': cert[2].hex(),
            'issueDate': cert[3],
            'signature': cert[4].hex(),
            'revoked': cert_data.get('revoked', False)
        }
    except Exception as e:
        logger.error(f"Lỗi khi tra cứu chứng chỉ: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/events")
async def get_events():
    """
    Lấy tất cả sự kiện chứng chỉ và admin từ MongoDB.

    Returns:
        dict: Danh sách sự kiện.
    """
    try:
        cert_events = mongo_client.find_all_certificates()
        admin_events = mongo_client.find_all_admins()
        return {
            'certificate_events': cert_events,
            'admin_events': admin_events
        }
    except Exception as e:
        logger.error(f"Lỗi khi lấy sự kiện: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))