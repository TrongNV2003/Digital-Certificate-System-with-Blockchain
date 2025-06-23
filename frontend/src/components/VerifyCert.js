import { useState } from 'react';
import { toast } from 'react-toastify';
import api from '../api';

function VerifyCert() {
  const [id, setId] = useState('');
  const [certData, setCertData] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await api.verifyCertificate(id);
      setCertData(response.data);
      toast.success('Tra cứu thành công');
    } catch (error) {
      setCertData(null);
      toast.error(error.response?.data?.detail || 'Lỗi khi tra cứu chứng chỉ');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h2 className="text-2xl font-bold mb-4">Tra cứu Chứng chỉ</h2>
      <form onSubmit={handleSubmit} className="max-w-md mx-auto bg-white p-6 rounded-lg shadow-md">
        <div className="mb-4">
          <label className="block text-gray-700">ID Chứng chỉ</label>
          <input
            type="text"
            value={id}
            onChange={(e) => setId(e.target.value)}
            className="w-full p-2 border rounded"
            required
          />
        </div>
        <button
          type="submit"
          className={`w-full bg-green-600 text-white p-2 rounded hover:bg-green-700 ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
          disabled={loading}
        >
          {loading ? 'Đang xử lý...' : 'Tra cứu'}
        </button>
      </form>
      {certData && (
        <div className="mt-6 max-w-md mx-auto bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-bold mb-2">Thông tin Chứng chỉ</h3>
          <p><strong>ID:</strong> {certData.id}</p>
          <p><strong>Người nhận:</strong> {certData.recipient}</p>
          <p><strong>Khóa học:</strong> {certData.course}</p>
          <p><strong>Ngày cấp:</strong> {new Date(certData.issueDate * 1000).toLocaleString()}</p>
          <p><strong>Trạng thái:</strong> {certData.revoked ? 'Đã thu hồi' : 'Hợp lệ'}</p>
          <p><strong>Recipient Hash:</strong> {certData.recipientHash}</p>
          <p><strong>Course Hash:</strong> {certData.courseHash}</p>
          <p><strong>Chữ ký:</strong> {certData.signature}</p>
        </div>
      )}
    </div>
  );
}

export default VerifyCert;