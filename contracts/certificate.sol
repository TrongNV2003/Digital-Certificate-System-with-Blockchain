// SPDX-License-Identifier: SEE LICENSE IN LICENSE
pragma solidity ^0.8.19;

contract Certificate {
    // Địa chỉ chủ sở hữu hợp đồng
    address public owner;

    // Cấu trúc chứng chỉ
    struct Cert {
        string id;              // ID duy nhất của chứng chỉ
        bytes32 recipientHash;  // Hash của tên người nhận
        bytes32 courseHash;     // Hash của tên khóa học
        uint256 issueDate;      // Ngày cấp
        bytes signature;        // Chữ ký số của người cấp
    }

    // Lưu trữ chứng chỉ theo ID
    mapping(string => Cert) public certificates;

    // Quản lý quyền admin
    mapping(address => bool) public admins;

    // Sự kiện khi chứng chỉ được cấp
    event CertificateIssued(string id, bytes32 recipientHash, bytes32 courseHash, uint256 issueDate, bytes signature);

    // Sự kiện khi chứng chỉ bị thu hồi
    event CertificateRevoked(string id);

    // Sự kiện khi admin được thêm/xóa
    event AdminAdded(address admin);
    event AdminRemoved(address admin);

    // Constructor: gán chủ hợp đồng và thêm admin đầu tiên
    constructor() {
        owner = msg.sender;
        admins[msg.sender] = true;
    }

    // Modifier: chỉ admin được gọi
    modifier onlyAdmin() {
        require(admins[msg.sender], "Only admin can call");
        _;
    }

    // Modifier: chỉ chủ hợp đồng được gọi
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call");
        _;
    }

    // Thêm admin mới
    function addAdmin(address newAdmin) public onlyOwner {
        admins[newAdmin] = true;
        emit AdminAdded(newAdmin);
    }

    // Xóa admin
    function removeAdmin(address adminAddress) public onlyOwner {
        admins[adminAddress] = false;
        emit AdminRemoved(adminAddress);
    }

    // Cấp chứng chỉ với xác minh chữ ký
    function issueCertificate(
        string memory id,
        bytes32 recipientHash,
        bytes32 courseHash,
        bytes memory signature
    ) public onlyAdmin {
        // Kiểm tra độ dài ID để giới hạn gas
        require(bytes(id).length <= 32, "ID too long");
        
        // Kiểm tra ID chứng chỉ chưa tồn tại
        require(bytes(certificates[id].id).length == 0, "Certificate ID already exists");
        
        // Xác minh chữ ký
        require(
            verifySignature(id, recipientHash, courseHash, signature, msg.sender),
            "Invalid signature"
        );

        // Lưu chứng chỉ
        certificates[id] = Cert(id, recipientHash, courseHash, block.timestamp, signature);
        
        // Kiểm tra trạng thái nội bộ: đảm bảo chứng chỉ đã được lưu
        assert(bytes(certificates[id].id).length > 0);
        
        // Phát sự kiện
        emit CertificateIssued(id, recipientHash, courseHash, block.timestamp, signature);
    }

    // Thu hồi chứng chỉ
    function revokeCertificate(string memory id) public onlyAdmin {
        require(bytes(certificates[id].id).length != 0, "Certificate does not exist");
        delete certificates[id];
        emit CertificateRevoked(id);
    }

    // Tra cứu chứng chỉ
    function verifyCertificate(string memory id) public view returns (Cert memory) {
        require(bytes(certificates[id].id).length != 0, "Certificate does not exist");
        return certificates[id];
    }

    // Hàm xác minh chữ ký
    function verifySignature(
        string memory id,
        bytes32 recipientHash,
        bytes32 courseHash,
        bytes memory signature,
        address signer
    ) internal pure returns (bool) {
        // Tạo message hash từ dữ liệu chứng chỉ
        bytes32 message = keccak256(abi.encodePacked(id, recipientHash, courseHash));
        // Thêm prefix Ethereum Signed Message
        bytes32 ethSignedMessage = keccak256(
            abi.encodePacked("\x19Ethereum Signed Message:\n32", message)
        );
        // Xác minh chữ ký
        return recoverSigner(ethSignedMessage, signature) == signer;
    }

    // Hàm khôi phục địa chỉ từ chữ ký
    function recoverSigner(bytes32 message, bytes memory signature) internal pure returns (address) {
        require(signature.length == 65, "Invalid signature length");
        bytes32 r;
        bytes32 s;
        uint8 v;
        // Tách chữ ký thành r, s, v
        assembly {
            r := mload(add(signature, 32))
            s := mload(add(signature, 64))
            v := byte(0, mload(add(signature, 96)))
        }
        // Đảm bảo v hợp lệ (27 hoặc 28)
        assert(v == 27 || v == 28);
        // Khôi phục địa chỉ
        return ecrecover(message, v, r, s);
    }
}