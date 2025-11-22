import api from './api';
import type {
  Word,
  WordCreate,
  WordUpdate,
  WordReviewRequest,
  WordReviewResponse,
  PartOfSpeech,
  CEFRLevel,
} from '~types';

export interface WordListParams {
  skip?: number;
  limit?: number;
  part_of_speech?: PartOfSpeech;
  cefr_level?: CEFRLevel;
  search?: string;
}

export const wordApi = {
  list: async (params: WordListParams = {}): Promise<Word[]> => {
    const { data } = await api.get<Word[]>('/words', { params });
    return data;
  },

  count: async (params: WordListParams = {}): Promise<number> => {
    const { data } = await api.get<{ count: number }>('/words/count', { params });
    return data.count;
  },

  get: async (id: number): Promise<Word> => {
    const { data } = await api.get<Word>(`/words/${id}`);
    return data;
  },

  create: async (word: WordCreate): Promise<Word> => {
    const { data } = await api.post<Word>('/words', word);
    return data;
  },

  update: async (id: number, word: WordUpdate): Promise<Word> => {
    const { data } = await api.put<Word>(`/words/${id}`, word);
    return data;
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/words/${id}`);
  },

  getDue: async (limit = 20): Promise<Word[]> => {
    const { data } = await api.get<Word[]>('/words/due', { params: { limit } });
    return data;
  },

  countDue: async (): Promise<number> => {
    const { data } = await api.get<{ count: number }>('/words/due/count');
    return data.count;
  },

  review: async (id: number, request: WordReviewRequest): Promise<WordReviewResponse> => {
    const { data } = await api.post<WordReviewResponse>(`/words/${id}/review`, request);
    return data;
  },

  bulkImport: async (words: string[]): Promise<{ imported: number; skipped_duplicates: number; words: Word[] }> => {
    const { data } = await api.post<{ imported: number; skipped_duplicates: number; words: Word[] }>(
      '/words/bulk-import',
      { words },
      { timeout: 5 * 60 * 1000 } // 5 minutes - bulk import processes words in chunks via Gemini
    );
    return data;
  },
};
