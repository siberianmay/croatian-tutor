import api from './api';
import type { AppSettings, AppSettingsUpdate, GeminiModel } from '~types';

export const settingsApi = {
  /**
   * Get current application settings.
   */
  get: async (): Promise<AppSettings> => {
    const { data } = await api.get<AppSettings>('/settings');
    return data;
  },

  /**
   * Update application settings (partial update).
   */
  update: async (settings: AppSettingsUpdate): Promise<AppSettings> => {
    const { data } = await api.patch<AppSettings>('/settings', settings);
    return data;
  },

  /**
   * Get list of available Gemini models.
   */
  getAvailableModels: async (): Promise<GeminiModel[]> => {
    const { data } = await api.get<GeminiModel[]>('/settings/models');
    return data;
  },
};
