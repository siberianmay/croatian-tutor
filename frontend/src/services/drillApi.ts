import api from './api';
import type {
  DrillSessionRequest,
  DrillSessionResponse,
  DrillAnswerRequest,
  DrillAnswerResponse,
} from '~types';

export const drillApi = {
  startSession: async (request: DrillSessionRequest): Promise<DrillSessionResponse> => {
    const { data } = await api.post<DrillSessionResponse>('/drills/start', request);
    return data;
  },

  checkAnswer: async (request: DrillAnswerRequest): Promise<DrillAnswerResponse> => {
    const { data } = await api.post<DrillAnswerResponse>('/drills/check', request);
    return data;
  },
};
