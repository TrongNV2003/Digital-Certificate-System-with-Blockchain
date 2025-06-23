import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Navbar from './components/Navbar';
import IssueCert from './components/IssueCert';
import RevokeCert from './components/RevokeCert';
import VerifyCert from './components/VerifyCert';
import Events from './components/Events';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        <Navbar />
        <Routes>
          <Route path="/" element={<IssueCert />} />
          <Route path="/revoke" element={<RevokeCert />} />
          <Route path="/verify" element={<VerifyCert />} />
          <Route path="/events" element={<Events />} />
        </Routes>
        <ToastContainer position="top-right" autoClose={3000} />
      </div>
    </Router>
  );
}

export default App;