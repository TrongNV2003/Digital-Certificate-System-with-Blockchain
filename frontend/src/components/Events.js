import { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import api from '../api';

function Events() {
  const [events, setEvents] = useState({ certificate_events: [], admin_events: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const response = await api.getEvents();
        if (!response.data || !Array.isArray(response.data.admin_events)) {
          throw new Error('Dữ liệu admin_events không hợp lệ');
        }
        setEvents(response.data);
        toast.success('Tải sự kiện thành công');
      } catch (error) {
        setError(error.response?.data?.detail || error.message || 'Lỗi khi tải sự kiện');
        toast.error(error.response?.data?.detail || error.message || 'Lỗi khi tải sự kiện');
      } finally {
        setLoading(false);
      }
    };
    fetchEvents();
  }, []);

  const truncateString = (str, startLen = 6, endLen = 4) => {
    if (typeof str !== 'string' || !str) {
      return 'N/A';
    }
    if (str.length < startLen + endLen) {
      return str;
    }
    return `${str.slice(0, startLen)}...${str.slice(-endLen)}`;
  };

  return (
    <div className="container mx-auto p-4">
      <h2 className="text-2xl font-bold mb-4">Sự kiện</h2>
      {error && <p className="text-red-500 mb-4">{error}</p>}
      {loading ? (
        <p>Đang tải...</p>
      ) : (
        <>
          <h3 className="text-lg font-bold mb-2">Sự kiện Chứng chỉ</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full bg-white shadow-md rounded">
              <thead>
                <tr className="bg-gray-200">
                  <th className="p-2 text-left">ID</th>
                  <th className="p-2 text-left">Người nhận</th>
                  <th className="p-2 text-left">Khóa học</th>
                  <th className="p-2 text-left">Sự kiện</th>
                  <th className="p-2 text-left">Trạng thái</th>
                </tr>
              </thead>
              <tbody>
                {events.certificate_events.map((event, index) => (
                  <tr key={event.id || index} className="border-t">
                    <td className="p-2">{event.id || 'N/A'}</td>
                    <td className="p-2">{event.recipient || 'N/A'}</td>
                    <td className="p-2">{event.course || 'N/A'}</td>
                    <td className="p-2">{event.event || 'N/A'}</td>
                    <td className="p-2">{event.revoked ? 'Đã thu hồi' : 'Hợp lệ'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <h3 className="text-lg font-bold mt-6 mb-2">Sự kiện Admin</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full bg-white shadow-md rounded">
              <thead>
                <tr className="bg-gray-200">
                  <th className="p-2 text-left">Địa chỉ</th>
                  <th className="p-2 text-left">Trạng thái</th>
                  <th className="p-2 text-left">TxHash</th>
                  <th className="p-2 text-left">Thời gian</th>
                  <th className="p-2 text-left">Sự kiện</th>
                </tr>
              </thead>
              <tbody>
                {events.admin_events.map((event, index) => {
                  if (typeof event !== 'object' || event === null) {
                    console.warn(`Dữ liệu admin_events không hợp lệ tại index ${index}:`, event);
                    return null;
                  }
                  return (
                    <tr key={(event.address && event.txHash) ? event.address + event.txHash : index} className="border-t">
                      <td className="p-2">{truncateString(event.address)}</td>
                      <td className="p-2">
                        {event.status === 'active' ? 'Hoạt động' : event.status === 'removed' ? 'Đã xóa' : 'N/A'}
                      </td>
                      <td className="p-2">
                        {event.txHash ? (
                          <a
                            href={`https://sepolia.etherscan.io/tx/${event.txHash}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-500 hover:underline"
                          >
                            {truncateString(event.txHash, 8, 4)}
                          </a>
                        ) : (
                          'N/A'
                        )}
                      </td>
                      <td className="p-2">
                        {event.timestamp && !isNaN(new Date(event.timestamp).getTime())
                          ? new Date(event.timestamp).toLocaleString()
                          : 'N/A'}
                      </td>
                      <td className="p-2">{event.event || 'N/A'}</td>
                    </tr>
                  );
                }).filter(Boolean)} {/* Loại bỏ null */}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}

export default Events;