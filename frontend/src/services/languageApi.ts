import api from './api';
import type { Language, LanguageSetting, LanguageSettingUpdate } from '~types';

export const languageApi = {
  /**
   * Get all active languages available for learning.
   */
  getLanguages: async (): Promise<Language[]> => {
    const { data } = await api.get<Language[]>('/languages');
    return data;
  },

  /**
   * Get a specific language by code.
   */
  getLanguage: async (code: string): Promise<Language> => {
    const { data } = await api.get<Language>(`/languages/${code}`);
    return data;
  },

  /**
   * Get user's current learning language.
   */
  getUserLanguage: async (): Promise<LanguageSetting> => {
    const { data } = await api.get<LanguageSetting>('/settings/language');
    return data;
  },

  /**
   * Set user's learning language.
   */
  setUserLanguage: async (update: LanguageSettingUpdate): Promise<LanguageSetting> => {
    const { data } = await api.patch<LanguageSetting>('/settings/language', update);
    return data;
  },
};
