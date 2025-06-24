import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { useState } from 'react';
import Navbar from './components/Navbar';
import IssueCert from './components/IssueCert';
import RevokeCert from './components/RevokeCert';
import VerifyCert from './components/VerifyCert';
import Events from './components/Events';
import Login from './components/Login';
import AdminManagement from './components/AdminManagement';

function App() {
  const [token, setToken] = useState(localStorage.getItem('token') || '');

  const handleLogout = () => {
    setToken('');
    localStorage.removeItem('token');
  };

  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        <Navbar setToken={setToken} handleLogout={handleLogout} />
        <Routes>
          <Route path="/" element={<IssueCert token={token} />} />
          <Route path="/revoke" element={<RevokeCert token={token} />} />
          <Route path="/verify" element={<VerifyCert />} />
          <Route path="/events" element={<Events />} />
          <Route path="/login" element={<Login setToken={setToken} />} />
          <Route path="/admin" element={<AdminManagement token={token} />} />
        </Routes>
        <ToastContainer position="top-right" autoClose={1500} />
      </div>
    </Router>
  );
}

export default App;