import api from './api';
import type {
  CEFRLevel,
  ConversationRequest,
  ConversationResponse,
  GrammarExerciseRequest,
  GrammarExerciseResponse,
  TranslationRequest,
  TranslationResponse,
  SentenceConstructionRequest,
  SentenceConstructionResponse,
  ReadingExerciseRequest,
  ReadingExerciseResponse,
  ReadingBatchEvaluateRequest,
  ReadingBatchEvaluateResponse,
  DialogueExerciseRequest,
  DialogueExerciseResponse,
  AnswerCheckRequest,
  AnswerCheckResponse,
  GrammarTopic,
  TopicProgress,
} from '~types';

export const exerciseApi = {
  // Conversation
  async conversation(
    request: ConversationRequest,
    cefrLevel: CEFRLevel = 'A1'
  ): Promise<ConversationResponse> {
    const response = await api.post<ConversationResponse>(
      `/exercises/conversation?cefr_level=${cefrLevel}`,
      request
    );
    return response.data;
  },

  // Grammar
  async generateGrammar(
    request: GrammarExerciseRequest = {},
    cefrLevel?: CEFRLevel
  ): Promise<GrammarExerciseResponse> {
    const params = cefrLevel ? `?cefr_level=${cefrLevel}` : '';
    const response = await api.post<GrammarExerciseResponse>(
      `/exercises/grammar${params}`,
      request
    );
    return response.data;
  },

  // Translation
  async generateTranslation(
    request: TranslationRequest
  ): Promise<TranslationResponse> {
    const response = await api.post<TranslationResponse>(
      '/exercises/translate',
      request
    );
    return response.data;
  },

  // Sentence Construction
  async generateSentenceConstruction(
    request: SentenceConstructionRequest = {}
  ): Promise<SentenceConstructionResponse> {
    const response = await api.post<SentenceConstructionResponse>(
      '/exercises/sentence-construction',
      request
    );
    return response.data;
  },

  // Reading Comprehension
  async generateReading(
    request: ReadingExerciseRequest = {}
  ): Promise<ReadingExerciseResponse> {
    const response = await api.post<ReadingExerciseResponse>(
      '/exercises/reading',
      request
    );
    return response.data;
  },

  async evaluateReadingBatch(
    request: ReadingBatchEvaluateRequest
  ): Promise<ReadingBatchEvaluateResponse> {
    const response = await api.post<ReadingBatchEvaluateResponse>(
      '/exercises/reading/evaluate-batch',
      request
    );
    return response.data;
  },

  // Dialogue
  async generateDialogue(
    request: DialogueExerciseRequest = {}
  ): Promise<DialogueExerciseResponse> {
    const response = await api.post<DialogueExerciseResponse>(
      '/exercises/dialogue',
      request
    );
    return response.data;
  },

  async dialogueTurn(
    exerciseId: string,
    userMessage: string,
    aiRole: string,
    scenario: string,
    history: Array<{ role: string; content: string }>,
    cefrLevel: CEFRLevel = 'A1'
  ): Promise<ConversationResponse> {
    const response = await api.post<ConversationResponse>(
      `/exercises/dialogue/turn?cefr_level=${cefrLevel}`,
      {
        exercise_id: exerciseId,
        user_message: userMessage,
        ai_role: aiRole,
        scenario,
        history,
      }
    );
    return response.data;
  },

  // Answer Evaluation
  async evaluate(request: AnswerCheckRequest): Promise<AnswerCheckResponse> {
    const response = await api.post<AnswerCheckResponse>(
      '/exercises/evaluate',
      request
    );
    return response.data;
  },

  // Session Management
  async endSession(
    exerciseType: string,
    variant: string = ''
  ): Promise<{ ended: boolean; message: string }> {
    const response = await api.post<{ ended: boolean; message: string }>(
      '/exercises/session/end',
      { exercise_type: exerciseType, variant }
    );
    return response.data;
  },
};

export const topicsApi = {
  async list(cefrLevel?: CEFRLevel): Promise<GrammarTopic[]> {
    const params = cefrLevel ? `?cefr_level=${cefrLevel}` : '';
    const response = await api.get<GrammarTopic[]>(`/topics${params}`);
    return response.data;
  },

  async get(topicId: number): Promise<GrammarTopic> {
    const response = await api.get<GrammarTopic>(`/topics/${topicId}`);
    return response.data;
  },

  async create(topic: Omit<GrammarTopic, 'id'>): Promise<GrammarTopic> {
    const response = await api.post<GrammarTopic>('/topics', topic);
    return response.data;
  },

  async generateDescription(topicId: number): Promise<GrammarTopic> {
    const response = await api.post<GrammarTopic>(
      `/topics/${topicId}/generate-description`
    );
    return response.data;
  },

  async getUserProgress(cefrLevel?: CEFRLevel): Promise<TopicProgress[]> {
    const params = cefrLevel ? `?cefr_level=${cefrLevel}` : '';
    const response = await api.get<TopicProgress[]>(`/topics/progress${params}`);
    return response.data;
  },
};
