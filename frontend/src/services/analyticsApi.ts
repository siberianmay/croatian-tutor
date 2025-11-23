import api from './api';
import type {
  LeechesResponse,
  ForecastResponse,
  VelocityResponse,
  DifficultyResponse,
  FullAnalytics,
} from '~types';

export const analyticsApi = {
  async getLeeches(limit: number = 20): Promise<LeechesResponse> {
    const response = await api.get<LeechesResponse>(`/analytics/leeches?limit=${limit}`);
    return response.data;
  },

  async getForecast(days: number = 7): Promise<ForecastResponse> {
    const response = await api.get<ForecastResponse>(`/analytics/forecast?days=${days}`);
    return response.data;
  },

  async getVelocity(): Promise<VelocityResponse> {
    const response = await api.get<VelocityResponse>('/analytics/velocity');
    return response.data;
  },

  async getDifficulty(): Promise<DifficultyResponse> {
    const response = await api.get<DifficultyResponse>('/analytics/difficulty');
    return response.data;
  },

  async getFullAnalytics(): Promise<FullAnalytics> {
    const response = await api.get<FullAnalytics>('/analytics/');
    return response.data;
  },
};
