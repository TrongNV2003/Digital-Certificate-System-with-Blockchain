import React from 'react';
import { Link } from 'react-router-dom';
import { toast } from 'react-toastify';

const Navbar = ({ handleLogout }) => {
  const token = localStorage.getItem('token');

  const onLogout = () => {
    handleLogout();
    toast.success('Đăng xuất thành công!');
  };

  return (
    <nav className="bg-blue-600 p-4 shadow-md">
      <ul className="flex space-x-6 justify-center text-white">
        <li>
          <Link to="/" className="hover:underline">Cấp chứng chỉ</Link>
        </li>
        <li>
          <Link to="/revoke" className="hover:underline">Thu hồi chứng chỉ</Link>
        </li>
        <li>
          <Link to="/verify" className="hover:underline">Tra cứu chứng chỉ</Link>
        </li>
        <li>
          <Link to="/events" className="hover:underline">Sự kiện</Link>
        </li>
        <li>
          <Link to="/admin" className="hover:underline">Quản lý Admin</Link>
        </li>
        {token ? (
          <li>
            <button onClick={onLogout} className="hover:underline">
              Đăng xuất
            </button>
          </li>
        ) : (
          <li>
            <Link to="/login" className="hover:underline">Đăng nhập</Link>
          </li>
        )}
      </ul>
    </nav>
  );
};

export default Navbar;