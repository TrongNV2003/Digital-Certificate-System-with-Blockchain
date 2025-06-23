import { useState } from 'react';
import { toast } from 'react-toastify';
import api from '../api';

function IssueCert() {
  const [formData, setFormData] = useState({
    id: '',
    recipient: '',
    course: '',
  });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await api.issueCertificate(formData);
      toast.success(response.data.message);
      setFormData({ id: '', recipient: '', course: '' });
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Lỗi khi cấp chứng chỉ');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h2 className="text-2xl font-bold mb-4">Cấp Chứng chỉ</h2>
      <form onSubmit={handleSubmit} className="max-w-md mx-auto bg-white p-6 rounded-lg shadow-md">
        <div className="mb-4">
          <label className="block text-gray-700">ID Chứng chỉ</label>
          <input
            type="text"
            name="id"
            value={formData.id}
            onChange={handleChange}
            className="w-full p-2 border rounded"
            required
          />
        </div>
        <div className="mb-4">
          <label className="block text-gray-700">Người nhận</label>
          <input
            type="text"
            name="recipient"
            value={formData.recipient}
            onChange={handleChange}
            className="w-full p-2 border rounded"
            required
          />
        </div>
        <div className="mb-4">
          <label className="block text-gray-700">Khóa học</label>
          <input
            type="text"
            name="course"
            value={formData.course}
            onChange={handleChange}
            className="w-full p-2 border rounded"
            required
          />
        </div>
        <button
          type="submit"
          className={`w-full bg-blue-600 text-white p-2 rounded hover:bg-blue-700 ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
          disabled={loading}
        >
          {loading ? 'Đang xử lý...' : 'Cấp Chứng chỉ'}
        </button>
      </form>
    </div>
  );
}

export default IssueCert;