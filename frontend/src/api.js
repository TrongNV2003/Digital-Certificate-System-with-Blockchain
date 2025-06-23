import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const api = {
  issueCertificate: async (data) => {
    return await axios.post(`${API_URL}/api/issue-certificate`, data);
  },
  revokeCertificate: async (data) => {
    return await axios.post(`${API_URL}/api/revoke-certificate`, data);
  },
  verifyCertificate: async (id) => {
    return await axios.get(`${API_URL}/api/verify-certificate/${id}`);
  },
  getEvents: async () => {
    return await axios.get(`${API_URL}/api/events`);
  },
};

export default api;