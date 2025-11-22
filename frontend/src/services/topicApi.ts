import api from './api';
import type { GrammarTopic, CEFRLevel } from '~types';

export interface TopicListParams {
  skip?: number;
  limit?: number;
  cefr_level?: CEFRLevel;
}

export const topicApi = {
  list: async (params?: TopicListParams): Promise<GrammarTopic[]> => {
    const { data } = await api.get<GrammarTopic[]>('/topics', { params });
    return data;
  },

  get: async (id: number): Promise<GrammarTopic> => {
    const { data } = await api.get<GrammarTopic>(`/topics/${id}`);
    return data;
  },

  markLearnt: async (id: number): Promise<GrammarTopic> => {
    const { data } = await api.post<GrammarTopic>(`/topics/${id}/mark-learnt`);
    return data;
  },

  generateDescription: async (id: number): Promise<GrammarTopic> => {
    const { data } = await api.post<GrammarTopic>(`/topics/${id}/generate-description`);
    return data;
  },

  count: async (cefr_level?: CEFRLevel): Promise<number> => {
    const { data } = await api.get<{ count: number }>('/topics/count', {
      params: cefr_level ? { cefr_level } : undefined,
    });
    return data.count;
  },
};
