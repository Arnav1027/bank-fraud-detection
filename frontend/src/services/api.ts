import axios, { AxiosInstance, AxiosError } from 'axios';

// Use relative path in production, localhost in development
const API_URL = process.env.REACT_APP_API_URL || 
  (process.env.NODE_ENV === 'production' ? '/api/v1' : 'http://localhost:7777/api/v1');

interface ApiConfig {
  baseURL: string;
  headers: Record<string, string>;
}

class ApiClient {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    const config: ApiConfig = {
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    };

    this.client = axios.create(config);
    this.loadToken();

    // Add token to requests
    this.client.interceptors.request.use((config) => {
      if (this.token) {
        config.headers.Authorization = `Bearer ${this.token}`;
      }
      return config;
    });

    // Handle 401 responses
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          this.logout();
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth endpoints
  async signup(email: string, password: string, fullName: string) {
    const response = await this.client.post('/auth/signup', {
      email,
      password,
      full_name: fullName,
    });
    const data = response.data;
    this.setToken(data.access_token);
    return data;
  }

  async login(email: string, password: string) {
    const response = await this.client.post('/auth/login', {
      email,
      password,
    });
    this.setToken(response.data.access_token);
    return response.data;
  }

  logout() {
    this.token = null;
    localStorage.removeItem('auth_token');
  }

  // Transaction endpoints
  async checkFraud(fraudCheckRequest: any) {
    const response = await this.client.post('/transactions/check', fraudCheckRequest);
    return response.data;
  }

  async listTransactions(params: any = {}) {
    const response = await this.client.get('/transactions/', { params });
    return response.data;
  }

  async getTransaction(id: number) {
    const response = await this.client.get(`/transactions/${id}`);
    return response.data;
  }

  async batchCheckFraud(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await this.client.post('/transactions/batch', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }

  // Analytics endpoints
  async getSummary(days = 7) {
    const response = await this.client.get('/analytics/summary', { params: { days } });
    return response.data;
  }

  async getAlerts(limit = 20) {
    const response = await this.client.get('/analytics/alerts', { params: { limit } });
    return response.data;
  }

  async getMetrics() {
    const response = await this.client.get('/analytics/metrics');
    return response.data;
  }

  // Helper methods
  private setToken(token: string) {
    this.token = token;
    localStorage.setItem('auth_token', token);
  }

  private loadToken() {
    this.token = localStorage.getItem('auth_token');
  }

  isAuthenticated(): boolean {
    return this.token !== null;
  }
}

export default new ApiClient();
