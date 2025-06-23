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
        if tx_receipt.status == 0:
            logger.error(f"Giao dịch cấp chứng chỉ ID {data.id} thất bại")
            raise HTTPException(status_code=500, detail="Giao dịch thất bại trên blockchain")

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
    """
    try:
        certificate = mongo_client.find_certificate(id)
        if not certificate:
            logger.error(f"Chứng chỉ ID {id} không tìm thấy trong database")
            raise HTTPException(status_code=404, detail="Chứng chỉ không tồn tại")
        
        cert_data = await blockchain_client.verify_certificate(id)
        if not cert_data:
            raise HTTPException(status_code=404, detail="Không tìm thấy dữ liệu gốc")
        
        if (certificate['recipientHash'] != cert_data[1].hex() or 
            certificate['courseHash'] != cert_data[2].hex() or 
            certificate['signature'] != cert_data[4].hex()):
            logger.error(f"Dữ liệu chứng chỉ ID {id} không khớp giữa MongoDB và blockchain")
            raise HTTPException(status_code=400, detail="Dữ liệu chứng chỉ không khớp")
        
        return {
            'id': cert_data[0],
            'recipient': certificate['recipient'],
            'recipientHash': cert_data[1].hex(),
            'course': certificate['course'],
            'courseHash': cert_data[2].hex(),
            'issueDate': cert_data[3],
            'signature': cert_data[4].hex(),
            'revoked': certificate["revoked"]
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