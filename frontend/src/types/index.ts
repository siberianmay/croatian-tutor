// Enums matching backend
export type PartOfSpeech =
  | 'noun' | 'verb' | 'adjective' | 'adverb' | 'pronoun'
  | 'preposition' | 'conjunction' | 'interjection' | 'numeral' | 'particle' | 'phrase';

export type Gender = 'masculine' | 'feminine' | 'neuter';

export type CEFRLevel = 'A1' | 'A2' | 'B1' | 'B2' | 'C1' | 'C2';

export type ExerciseType =
  | 'vocabulary_cr_en' | 'vocabulary_en_cr' | 'vocabulary_fill_blank'
  | 'conversation' | 'grammar' | 'sentence_construction'
  | 'reading' | 'dialogue' | 'translation_cr_en' | 'translation_en_cr';

// Word types
export interface Word {
  id: number;
  user_id: number;
  croatian: string;
  english: string;
  part_of_speech: PartOfSpeech;
  gender: Gender | null;
  cefr_level: CEFRLevel;
  mastery_score: number;
  ease_factor: number;
  correct_count: number;
  wrong_count: number;
  next_review_at: string | null;
  last_reviewed_at: string | null;
  created_at: string;
}

export interface WordCreate {
  croatian: string;
  english: string;
  part_of_speech: PartOfSpeech;
  gender?: Gender | null;
  cefr_level: CEFRLevel;
}

export interface WordUpdate {
  croatian?: string;
  english?: string;
  part_of_speech?: PartOfSpeech;
  gender?: Gender | null;
  cefr_level?: CEFRLevel;
}

export interface WordReviewRequest {
  correct: boolean;
  response_time_ms?: number;
}

export interface WordReviewResponse {
  word_id: number;
  new_mastery_score: number;
  next_review_at: string | null;
  correct_count: number;
  wrong_count: number;
}

// Drill types
export interface DrillItem {
  word_id: number;
  prompt: string;
  expected_answer: string;
  part_of_speech: string;
  gender: string | null;
  cefr_level: string | null;
}

export interface DrillSessionRequest {
  exercise_type: 'vocabulary_cr_en' | 'vocabulary_en_cr';
  count: number;
}

export interface DrillSessionResponse {
  exercise_type: string;
  items: DrillItem[];
  total_count: number;
}

export interface DrillAnswerRequest {
  word_id: number;
  user_answer: string;
  exercise_type: 'vocabulary_cr_en' | 'vocabulary_en_cr';
}

export interface DrillAnswerResponse {
  correct: boolean;
  expected_answer: string;
  user_answer: string;
  word_id: number;
}

// Progress types
export interface UserProgress {
  total_words_learned: number;
  total_exercises_completed: number;
  accuracy_rate: number;
  streak_days: number;
}
