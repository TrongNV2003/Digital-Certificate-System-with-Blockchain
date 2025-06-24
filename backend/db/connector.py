from datetime import datetime
from loguru import logger
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from typing import List, Dict, Any, Optional

from backend.config.setting import db_config


class MongoDBClient:
    def __init__(self, uri: str = db_config.mongodb_uri, db_name: str = db_config.db_name):
        """
        Initialize MongoDB client.
        Args:
            uri (str): MongoDB connection URI.
            db_name (str): Database name.
        """
        try:
            self.client = MongoClient(uri)
            self.db = self.client[db_name]
            self.cert_collection = self.db[db_config.collection_name]
            self.admin_collection = self.db[db_config.admin_collection_name]
            self.admin_log_collection = self.db[db_config.admin_log_collection_name]
            
            self.client.admin.command("ping")
            logger.info(f"Connected to MongoDB at {uri}, database: {db_name}")
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise

    def insert_certificate(self, certificate: Dict[str, Any]) -> str:
        """
        Insert a certificate into MongoDB.

        Args:
            certificate (Dict[str, Any]): Certificate data to insert.

        Returns:
            str: Inserted product ID.
        """
        try:
            result = self.cert_collection.insert_one(certificate)
            logger.info(f"Add cerificate ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Lỗi khi thêm chứng chỉ: {str(e)}")
            raise

    def update_certificate(self, cert_id: str, update_data: Dict[str, Any]) -> None:
        """
        Update certificate MongoDB.

        Args:
            cert_id (str): certificate ID.
            update_data (Dict[str, Any]): Dữ liệu cần cập nhật.
        """
        try:
            result = self.cert_collection.update_one(
                {"id": cert_id}, {"$set": update_data}
            )
            if result.matched_count == 0:
                logger.warning(f"Not found cerificate ID: {cert_id}")
            else:
                logger.info(f"Update certificate ID: {cert_id}")
        except Exception as e:
            logger.error(f"Lỗi khi cập nhật chứng chỉ: {str(e)}")
            raise


    def find_certificate(self, cert_id: str) -> Optional[Dict[str, Any]]:
        """
        Find certificate with ID.

        Args:
            cert_id (str): certificate ID.

        Returns:
            Optional[Dict[str, Any]]: Dữ liệu chứng chỉ hoặc None nếu không tìm thấy.
        """
        try:
            cert = self.cert_collection.find_one({"id": cert_id})
            if cert:
                if "_id" in cert:
                    cert["_id"] = str(cert["_id"])
                logger.debug(f"Found Cerificate ID: {cert_id}")
                return cert
            logger.warning(f"Not found cerificate ID: {cert_id}")
            return None
        except Exception as e:
            logger.error(f"Lỗi khi tìm chứng chỉ: {str(e)}")
            raise

    def find_all_certificates(self) -> List[Dict[str, Any]]:
        """
        Find all certificates.

        Returns:
            List[Dict[str, Any]]: List certificates.
        """
        try:
            certificates = self.cert_collection.find({})
            result = []
            for cert in certificates:
                if "_id" in cert:
                    cert["_id"] = str(cert["_id"])
                result.append(cert)
            logger.debug(f"Found {len(result)} certificates")
            return result
        except Exception as e:
            logger.error(f"Lỗi khi lấy danh sách chứng chỉ: {str(e)}")
            raise

    def update_admin(self, admin_address: str, status: str, tx_hash: str = None, event: str = None) -> None:
        """
        Update admin status.

        Args:
            admin_address (str): Địa chỉ ví của admin.
            status (str): Trạng thái ('active' hoặc 'removed').
        """
        try:
            update_data = {
            "address": admin_address,
            "status": status,
            "timestamp": int(datetime.utcnow().timestamp())
            }
            if tx_hash:
                update_data["txHash"] = tx_hash
            if event:
                update_data["event"] = event
            self.admin_collection.update_one(
                {"address": admin_address},
                {"$set": update_data},
                upsert=True
            )
            logger.info(f"Update admin {admin_address} with status: {status}")
        except Exception as e:
            logger.error(f"Lỗi khi cập nhật admin: {str(e)}")
            raise

    def find_all_admins(self) -> List[Dict[str, Any]]:
        """
        Find all admins MongoDB.

        Returns:
            List[Dict[str, Any]]: List admin.
        """
        try:
            admins = self.admin_collection.find({})
            result = []
            for admin in admins:
                if not isinstance(admin, dict):
                    logger.warn(f"Bản ghi admin không hợp lệ: {admin}")
                    continue
                if "_id" in admin:
                    admin["_id"] = str(admin["_id"])
                # Đảm bảo các trường cần thiết
                required_fields = ['address', 'status', 'txHash', 'timestamp', 'event']
                for field in required_fields:
                    if field not in admin:
                        logger.warn(f"Thiếu trường {field} trong admin: {admin}")
                        admin[field] = None
                result.append(admin)
            logger.debug(f"Found {len(result)} admins")
            return result
        except Exception as e:
            logger.error(f"Lỗi khi lấy danh sách admin: {str(e)}")
            raise

    def insert_admin_log(self, admin_data: Dict[str, Any]) -> None:
        """
        Insert admin log into MongoDB.

        Args:
            admin_data (Dict[str, Any]): Admin log data (address, status, txHash, timestamp, event).
        """
        try:
            self.admin_log_collection.insert_one(admin_data)
            logger.info(f"Inserted admin log for {admin_data['address']}")
        except Exception as e:
            logger.error(f"Lỗi khi lưu admin log: {str(e)}")
            raise