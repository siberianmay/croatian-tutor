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

// Grammar Topic types
export interface GrammarTopic {
  id: number;
  name: string;
  cefr_level: CEFRLevel;
  prerequisite_ids: number[] | null;
  rule_description: string | null;
  display_order: number;
}

export interface TopicProgress {
  topic_id: number;
  topic_name: string;
  cefr_level: CEFRLevel;
  mastery_score: number;
  times_practiced: number;
}

// Conversation types
export interface ConversationTurn {
  role: 'user' | 'assistant';
  content: string;
}

export interface ConversationRequest {
  message: string;
  history: ConversationTurn[];
}

export interface ConversationResponse {
  response: string;
  corrections: Array<{
    original: string;
    corrected: string;
    explanation: string;
  }> | null;
  new_vocabulary: string[] | null;
}

// Grammar Exercise types
export interface GrammarExerciseRequest {
  topic_id?: number;
}

export interface GrammarExerciseResponse {
  exercise_id: string;
  topic_name: string;
  instruction: string;
  question: string;
  hints: string[] | null;
}

// Translation types
export interface TranslationRequest {
  direction: 'cr_en' | 'en_cr';
  cefr_level?: CEFRLevel;
}

export interface TranslationResponse {
  exercise_id: string;
  source_text: string;
  source_language: string;
  target_language: string;
}

// Sentence Construction types
export interface SentenceConstructionRequest {
  cefr_level?: CEFRLevel;
}

export interface SentenceConstructionResponse {
  exercise_id: string;
  words: string[];
  hint: string;
}

// Reading Comprehension types
export interface ReadingExerciseRequest {
  cefr_level?: CEFRLevel;
}

export interface ReadingExerciseResponse {
  exercise_id: string;
  passage: string;
  questions: Array<{
    question: string;
    expected_answer: string;
  }>;
}

// Dialogue types
export interface DialogueExerciseRequest {
  cefr_level?: CEFRLevel;
  scenario?: string;
}

export interface DialogueExerciseResponse {
  exercise_id: string;
  scenario: string;
  dialogue_start: string;
  user_role: string;
  ai_role: string;
  suggested_phrases: string[];
}

// Answer Evaluation types
export interface AnswerCheckRequest {
  exercise_type: ExerciseType;
  user_answer: string;
  expected_answer: string;
  context?: string;
  topic_id?: number;
}

export interface AnswerCheckResponse {
  correct: boolean;
  score: number;
  feedback: string;
  correct_answer: string | null;
  error_category: string | null;
  explanation: string | null;
}

// Progress/Dashboard types
export interface ProgressSummary {
  total_words: number;
  mastered_words: number;
  words_due_today: number;
  total_exercises: number;
  total_errors: number;
  streak_days: number;
  current_level: CEFRLevel;
}

export interface VocabularyStats {
  by_level: Record<CEFRLevel, number>;
  by_mastery: {
    new: number;
    learning: number;
    mastered: number;
  };
  recent_words: Array<{
    croatian: string;
    english: string;
    mastery_score: number;
  }>;
}

export interface TopicStatItem {
  id: number;
  name: string;
  level: CEFRLevel;
  mastery: number;
  attempts: number;
}

export interface TopicStats {
  total_topics: number;
  practiced_topics: number;
  mastered_topics: number;
  topics: TopicStatItem[];
}

export interface DailyActivity {
  date: string;
  exercises: number;
  duration_minutes: number;
}

export interface ActivityStats {
  daily_activity: DailyActivity[];
  exercise_breakdown: Record<string, number>;
}

export interface WeakArea {
  category: string;
  count: number;
  suggestion: string;
}

export interface RecentError {
  category: string;
  details: string | null;
  correction: string | null;
  date: string;
}

export interface ErrorPatterns {
  by_category: Record<string, number>;
  recent_errors: RecentError[];
  weak_areas: WeakArea[];
}
