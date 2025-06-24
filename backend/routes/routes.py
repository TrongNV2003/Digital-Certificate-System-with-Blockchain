import os
import jwt
import bcrypt
import asyncio
from loguru import logger
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from backend.db.connector import MongoDBClient
from backend.blockchain.blockchain import BlockchainClient
from backend.utils.utils import CertificateInput, RevokeInput, AdminInput

router = APIRouter(prefix="/api", tags=["Certificate"])

mongo_client = MongoDBClient()
blockchain_client = BlockchainClient()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

SECRET_KEY = os.getenv("JWT_SECRET_KEY")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        # Nếu hashed_password là chuỗi, encode thành bytes
        if isinstance(hashed_password, str):
            hashed_password_bytes = hashed_password.encode('utf-8')
        else:
            hashed_password_bytes = hashed_password
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password_bytes)
    except ValueError as e:
        logger.error(f"Lỗi xác thực mật khẩu: {str(e)}")
        return False

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if payload.get("role") != "super_admin":
            raise HTTPException(status_code=403, detail="Không có quyền admin")
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Token không hợp lệ")

# API tạo token
@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Tạo token JWT cho người dùng.

    Args:
        form_data: Username và password từ form.

    Returns:
        dict: Token JWT và loại token.
    """
    try:
        user = mongo_client.user_collection.find_one({"username": form_data.username})
        if not user or not verify_password(form_data.password, user["password"]):
            raise HTTPException(status_code=401, detail="Tên người dùng hoặc mật khẩu không đúng")
        if user.get("role") != "super_admin":
            raise HTTPException(status_code=403, detail="Không có quyền admin")
        
        token_data = {
            "sub": form_data.username,
            "role": user["role"],
            "exp": datetime.utcnow() + timedelta(minutes=30)
        }
        token = jwt.encode(token_data, SECRET_KEY, algorithm="HS256")
        logger.info(f"Đã cấp token cho {form_data.username}")
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Lỗi khi tạo token: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/issue-certificate")
async def issue_certificate(data: CertificateInput, payload=Depends(verify_token)):
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
        
        await asyncio.sleep(10)
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
async def revoke_certificate(data: RevokeInput, payload=Depends(verify_token)):
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
            'message': 'Thu hồi chứng chỉ thành công',
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
        
        # cert_data = await blockchain_client.verify_certificate(id)
        # if not cert_data:
        #     raise HTTPException(status_code=404, detail="Không tìm thấy dữ liệu gốc")
        
        # if (certificate['recipientHash'] != cert_data[1].hex() or 
        #     certificate['courseHash'] != cert_data[2].hex() or 
        #     certificate['signature'] != cert_data[4].hex()):
        #     logger.error(f"Dữ liệu chứng chỉ ID {id} không khớp giữa MongoDB và blockchain")
        #     raise HTTPException(status_code=400, detail="Dữ liệu chứng chỉ không khớp")
        
        return {
            'id': certificate['id'],
            'recipient': certificate['recipient'],
            'recipientHash': certificate['recipientHash'][:18] + '...' + certificate['recipientHash'][-8:],
            'course': certificate['course'],
            'courseHash': certificate['courseHash'][:18] + '...' + certificate['courseHash'][-8:],
            'issueDate': certificate['issueDate'],
            'signature': certificate['signature'][:18] + '...' + certificate['signature'][-8:],
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
    

@router.post("/add-admin")
async def add_admin(data: AdminInput, payload=Depends(verify_token)):
    try:
        if not data.address.startswith('0x') or len(data.address) != 42:
            raise ValueError("Địa chỉ admin không hợp lệ")
        
        tx_receipt = await blockchain_client.add_admin(data.address)
        tx_hash = tx_receipt['transactionHash'].hex()
        mongo_client.update_admin(data.address, 'active', tx_hash=tx_hash, event='AdminAdded')
        
        admin_data = {
            'address': data.address,
            'status': 'active',
            'txHash': tx_hash,
            'timestamp': int(datetime.utcnow().timestamp()),
            'event': 'AdminAdded'
        }
        mongo_client.insert_admin_log(admin_data)
        short_tx_hash = f"{tx_hash[:8]}...{tx_hash[-4:]}"
        return {
            'message': 'Thêm admin thành công',
            'txHash': short_tx_hash
        }
    except Exception as e:
        logger.error(f"Lỗi khi thêm admin: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/remove-admin")
async def remove_admin(data: AdminInput, payload=Depends(verify_token)):
    """
    Xóa admin khỏi smart contract và MongoDB.

    Args:
        data (AdminInput): Địa chỉ admin cần xóa.
        request (Request): Thông tin yêu cầu HTTP.
        token (str): JWT token xác thực.

    Returns:
        dict: Thông báo và txHash.
    """
    try:
        if not data.address.startswith('0x') or len(data.address) != 42:
            raise ValueError("Địa chỉ admin không hợp lệ")
        
        tx_receipt = await blockchain_client.remove_admin(data.address)
        tx_hash = tx_receipt['transactionHash'].hex()
        mongo_client.update_admin(data.address, 'removed', tx_hash=tx_hash, event='AdminRemoved')

        admin_data = {
            'address': str(data.address),
            'status': 'removed',
            'txHash': tx_hash,
            'timestamp': int(datetime.utcnow().timestamp()),
            'event': 'AdminRemoved'
        }
        mongo_client.insert_admin_log(admin_data)
        short_tx_hash = f"{tx_hash[:8]}...{tx_hash[-4:]}"
        return {
            'message': 'Xóa admin thành công',
            'txHash': short_tx_hash
        }
    except Exception as e:
        logger.error(f"Lỗi khi xóa admin: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
