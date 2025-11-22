"""Enum definitions for the Croatian Tutor application."""

import enum


class PartOfSpeech(str, enum.Enum):
    """Parts of speech for vocabulary words."""

    NOUN = "noun"
    VERB = "verb"
    ADJECTIVE = "adjective"
    ADVERB = "adverb"
    PRONOUN = "pronoun"
    PREPOSITION = "preposition"
    CONJUNCTION = "conjunction"
    INTERJECTION = "interjection"
    NUMERAL = "numeral"
    PARTICLE = "particle"
    PHRASE = "phrase"  # For common short phrases


class Gender(str, enum.Enum):
    """Grammatical gender for nouns."""

    MASCULINE = "masculine"
    FEMININE = "feminine"
    NEUTER = "neuter"


class CEFRLevel(str, enum.Enum):
    """Common European Framework of Reference language levels."""

    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"


class ExerciseType(str, enum.Enum):
    """Types of exercises available in the app."""

    VOCABULARY_CR_EN = "vocabulary_cr_en"  # Croatian to English
    VOCABULARY_EN_CR = "vocabulary_en_cr"  # English to Croatian
    VOCABULARY_FILL_BLANK = "vocabulary_fill_blank"  # Fill in the blank
    CONVERSATION = "conversation"  # Free conversation with tutor
    GRAMMAR = "grammar"  # Grammar exercises
    SENTENCE_CONSTRUCTION = "sentence_construction"  # Build sentences
    READING = "reading"  # Reading comprehension
    DIALOGUE = "dialogue"  # Situational dialogues
    TRANSLATION_CR_EN = "translation_cr_en"  # Sentence translation CR->EN
    TRANSLATION_EN_CR = "translation_en_cr"  # Sentence translation EN->CR


class ErrorCategory(str, enum.Enum):
    """Categories of errors for tracking patterns."""

    CASE_ERROR = "case_error"  # Wrong grammatical case
    GENDER_AGREEMENT = "gender_agreement"  # Gender mismatch
    VERB_CONJUGATION = "verb_conjugation"  # Wrong verb form
    WORD_ORDER = "word_order"  # Incorrect word order
    SPELLING = "spelling"  # Spelling mistakes
    VOCABULARY = "vocabulary"  # Wrong word choice
    ACCENT = "accent"  # Missing or wrong accent marks
    OTHER = "other"  # Other errors
