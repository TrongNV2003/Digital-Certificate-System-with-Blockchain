import React, { useState } from 'react';
import { toast } from 'react-toastify';
import api from '../api';

const AdminManagement = ({ token }) => {
  const [adminAddress, setAdminAddress] = useState('');
  const [loading, setLoading] = useState(false);

  const handleAddAdmin = async (e) => {
    e.preventDefault();
    if (!token) {
      toast.error('Vui lòng đăng nhập trước!');
      return;
    }
    setLoading(true);
    try {
      const response = await api.addAdmin(adminAddress, token);
      toast.success(`Thêm admin thành công! TxHash: ${response.data.txHash}`);
      setAdminAddress('');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Lỗi khi thêm admin');
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveAdmin = async (e) => {
    e.preventDefault();
    if (!token) {
      toast.error('Vui lòng đăng nhập trước!');
      return;
    }
    setLoading(true);
    try {
      const response = await api.removeAdmin(adminAddress, token);
      toast.success(`Xóa admin thành công! TxHash: ${response.data.txHash}`);
      setAdminAddress('');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Lỗi khi xóa admin');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h2 className="text-2xl font-bold mb-4 text-center">Quản lý Admin</h2>
      {!token && (
        <p className="text-red-500 text-center mb-4">Vui lòng đăng nhập để quản lý admin.</p>
      )}
      <div className="max-w-md mx-auto bg-white p-6 rounded-lg shadow-md space-y-6">
        <form onSubmit={handleAddAdmin} className="space-y-4">
          <div>
            <label className="block text-gray-700">Địa chỉ Admin</label>
            <input
              type="text"
              value={adminAddress}
              onChange={(e) => setAdminAddress(e.target.value)}
              className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-green-500"
              placeholder="0x..."
              required
            />
          </div>
          <button
            type="submit"
            className={`w-full bg-green-600 text-white p-2 rounded hover:bg-green-700 ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
            disabled={loading || !token}
          >
            {loading ? 'Đang xử lý...' : 'Thêm Admin'}
          </button>
        </form>
        <form onSubmit={handleRemoveAdmin} className="space-y-4">
          <div>
            <label className="block text-gray-700">Địa chỉ Admin</label>
            <input
              type="text"
              value={adminAddress}
              onChange={(e) => setAdminAddress(e.target.value)}
              className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-red-500"
              placeholder="0x..."
              required
            />
          </div>
          <button
            type="submit"
            className={`w-full bg-red-600 text-white p-2 rounded hover:bg-red-700 ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
            disabled={loading || !token}
          >
            {loading ? 'Đang xử lý...' : 'Xóa Admin'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default AdminManagement;