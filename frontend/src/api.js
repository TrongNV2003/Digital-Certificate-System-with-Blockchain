import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const api = {
  login: async (username, password) => {
    return await axios.post(
      `${API_URL}/api/token`,
      new URLSearchParams({ username, password }),
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      }
    );
  },

  addAdmin: async (address, token) => {
    return await axios.post(
      `${API_URL}/api/add-admin`,
      { address },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
  },

  removeAdmin: async (address, token) => {
    return await axios.post(
      `${API_URL}/api/remove-admin`,
      { address },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
  },

  issueCertificate: async (data, token, config = {}) => {
    return await axios.post(
      `${API_URL}/api/issue-certificate`,
      data,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
        ...config
      }
    );
  },

  revokeCertificate: async (data, token) => {
    return await axios.post(
      `${API_URL}/api/revoke-certificate`,
      data,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
  },

  verifyCertificate: async (id) => {
    return await axios.get(`${API_URL}/api/verify-certificate/${id}`);
  },
  getEvents: async () => {
    return await axios.get(`${API_URL}/api/events`);
  },
};

export default api;