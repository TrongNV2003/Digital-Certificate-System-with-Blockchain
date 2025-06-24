import { useState } from 'react';
import { toast } from 'react-toastify';
import api from '../api';

function RevokeCert({ token }) {
  const [id, setId] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!token) {
      toast.error('Vui lòng đăng nhập trước!');
      return;
    }
    setLoading(true);
    try {
      const response = await api.revokeCertificate({ id }, token);
      toast.success(`Thu hồi chứng chỉ thành công! TxHash: ${response.data.txHash}`);
      setId('');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Lỗi khi thu hồi chứng chỉ');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h2 className="text-2xl font-bold mb-4">Thu hồi Chứng chỉ</h2>
      {!token && (
        <p className="text-red-500 text-center mb-4">Vui lòng đăng nhập để thu hồi chứng chỉ.</p>
      )}
      <form onSubmit={handleSubmit} className="max-w-md mx-auto bg-white p-6 rounded-lg shadow-md">
        <div className="mb-4">
          <label className="block text-gray-700">ID Chứng chỉ</label>
          <input
            type="text"
            value={id}
            onChange={(e) => setId(e.target.value)}
            className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-red-500"
            required
          />
        </div>
        <button
          type="submit"
          className={`w-full bg-red-600 text-white p-2 rounded hover:bg-red-700 ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
          disabled={loading || !token}
        >
          {loading ? 'Đang xử lý...' : 'Thu hồi Chứng chỉ'}
        </button>
      </form>
    </div>
  );
}

export default RevokeCert;