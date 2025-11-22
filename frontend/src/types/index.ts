// Word/Vocabulary types
export interface Word {
  id: number;
  croatian: string;
  english: string;
  pronunciation: string | null;
  topic_id: number;
  difficulty: number;
  notes: string | null;
  created_at: string;
}

// Topic types
export interface Topic {
  id: number;
  name: string;
  description: string | null;
  order: number;
  created_at: string;
}

// Exercise types
export type ExerciseType = 'translation' | 'multiple_choice' | 'fill_blank' | 'conversation';

export interface Exercise {
  id: number;
  type: ExerciseType;
  question: string;
  correct_answer: string;
  options: string[] | null;
  word_id: number | null;
  topic_id: number | null;
  difficulty: number;
}

// Learning session types
export interface LearningSession {
  id: number;
  user_id: number;
  started_at: string;
  ended_at: string | null;
  exercises_completed: number;
  correct_answers: number;
}

// Chat/Conversation types
export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface ConversationRequest {
  message: string;
  topic_id?: number;
  difficulty?: number;
}

export interface ConversationResponse {
  response: string;
  corrections?: string[];
  suggestions?: string[];
}

// Progress types
export interface UserProgress {
  total_words_learned: number;
  total_exercises_completed: number;
  accuracy_rate: number;
  streak_days: number;
  topics_completed: number[];
}
