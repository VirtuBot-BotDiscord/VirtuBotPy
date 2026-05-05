import axios from 'axios';

const adminId = import.meta.env.VITE_ADMIN_USER_ID;

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
});

api.interceptors.request.use((config) => {
  if (adminId) {
    config.headers = {
      ...config.headers,
      'X-User-ID': adminId
    };
  }
  return config;
});

const handleError = (error) => {
  if (error.response && error.response.data) {
    return new Error(error.response.data.error || error.response.statusText || 'Erreur API');
  }
  return new Error(error.message || 'Erreur inconnue');
};

export async function fetchBotStats() {
  try {
    const response = await api.get('/bot/stats');
    return response.data;
  } catch (error) {
    throw handleError(error);
  }
}

export async function fetchGuilds() {
  try {
    const response = await api.get('/guilds');
    return response.data;
  } catch (error) {
    throw handleError(error);
  }
}

export async function fetchCommands() {
  try {
    const response = await api.get('/bot/commands');
    return response.data;
  } catch (error) {
    throw handleError(error);
  }
}

export async function fetchLogs() {
  try {
    const response = await api.get('/logs');
    return response.data;
  } catch (error) {
    throw handleError(error);
  }
}

export async function clearLogs() {
  try {
    const response = await api.post('/admin/logs/clear');
    return response.data;
  } catch (error) {
    throw handleError(error);
  }
}

export async function fetchAdminStats() {
  try {
    const response = await api.get('/admin/stats');
    return response.data;
  } catch (error) {
    throw handleError(error);
  }
}

export async function restartBot() {
  try {
    const response = await api.post('/admin/restart');
    return response.data;
  } catch (error) {
    throw handleError(error);
  }
}
