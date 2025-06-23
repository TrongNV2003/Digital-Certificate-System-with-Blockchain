import { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import api from '../api';

function Events() {
  const [events, setEvents] = useState({ certificate_events: [], admin_events: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const response = await api.getEvents();
        setEvents(response.data);
        toast.success('Tải sự kiện thành công');
      } catch (error) {
        toast.error(error.response?.data?.detail || 'Lỗi khi tải sự kiện');
      } finally {
        setLoading(false);
      }
    };
    fetchEvents();
  }, []);

  return (
    <div className="container mx-auto p-4">
      <h2 className="text-2xl font-bold mb-4">Sự kiện</h2>
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
                {events.certificate_events.map((event) => (
                  <tr key={event.id} className="border-t">
                    <td className="p-2">{event.id}</td>
                    <td className="p-2">{event.recipient}</td>
                    <td className="p-2">{event.course}</td>
                    <td className="p-2">{event.event}</td>
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
                </tr>
              </thead>
              <tbody>
                {events.admin_events.map((event) => (
                  <tr key={event.address} className="border-t">
                    <td className="p-2">{event.address}</td>
                    <td className="p-2">{event.status === 'active' ? 'Hoạt động' : 'Đã xóa'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}

export default Events;