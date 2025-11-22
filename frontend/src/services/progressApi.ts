import api from './api';
import type {
  ProgressSummary,
  VocabularyStats,
  TopicStats,
  ActivityStats,
  ErrorPatterns,
} from '~types';

export const progressApi = {
  async getSummary(): Promise<ProgressSummary> {
    const response = await api.get<ProgressSummary>('/progress/summary');
    return response.data;
  },

  async getVocabularyStats(): Promise<VocabularyStats> {
    const response = await api.get<VocabularyStats>('/progress/vocabulary');
    return response.data;
  },

  async getTopicStats(): Promise<TopicStats> {
    const response = await api.get<TopicStats>('/progress/topics');
    return response.data;
  },

  async getActivity(days: number = 14): Promise<ActivityStats> {
    const response = await api.get<ActivityStats>(`/progress/activity?days=${days}`);
    return response.data;
  },

  async getErrorPatterns(): Promise<ErrorPatterns> {
    const response = await api.get<ErrorPatterns>('/progress/errors');
    return response.data;
  },

  async getContextSummary(): Promise<{ context: string }> {
    const response = await api.get<{ context: string }>('/progress/context');
    return response.data;
  },
};
