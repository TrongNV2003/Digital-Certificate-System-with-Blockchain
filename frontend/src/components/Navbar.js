import { Link } from 'react-router-dom';

function Navbar() {
  return (
    <nav className="bg-blue-600 p-4 shadow-md">
      <div className="container mx-auto flex justify-between items-center">
        <h1 className="text-white text-xl font-bold">Hệ thống Chứng chỉ Số</h1>
        <div className="space-x-4">
          <Link to="/" className="text-white hover:text-gray-200">Cấp Chứng chỉ</Link>
          <Link to="/revoke" className="text-white hover:text-gray-200">Thu hồi</Link>
          <Link to="/verify" className="text-white hover:text-gray-200">Tra cứu</Link>
          <Link to="/events" className="text-white hover:text-gray-200">Sự kiện</Link>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;