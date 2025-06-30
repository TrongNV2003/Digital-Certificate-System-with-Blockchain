```mermaid
graph TD
    A[Người dùng <br> Super Admin] -->|Nhập id| B[Frontend <br> React]
    B -->|POST /api/revoke-certificate <br> id, token| C[Backend <br> FastAPI]
    C -->|Xác thực token <br> verify_token| E[BlockchainClient]
    E -->|Kết nối qua Infura <br> sepolia.infura.io| I[Blockchain <br> Sepolia Testnet]
    E -->|Gửi giao dịch <br> revokeCertificate| H[Smart Contract]
    H -->|Kiểm tra onlyAdmin <br> Xóa certificates_id| I
    I -->|Trả về tx_receipt| E
    E -->|Trả về kết quả| C
    C -->|Cập nhật revoked=true| D[MongoDB]
    C -->|Trả về thông báo| B
    B -->|Hiển thị thông báo| A
```