import React, { Suspense, lazy } from 'react';
import { Routes, Route } from 'react-router-dom';
import { LoadingOverlay } from '@mantine/core';

import { AppLayout } from '~components/layout/AppLayout';
import ErrorBoundary from '~components/ErrorBoundary';

const HomePage = lazy(() => import('./pages/HomePage'));
const LearnPage = lazy(() => import('./pages/LearnPage'));
const VocabularyPage = lazy(() => import('./pages/VocabularyPage'));
const GrammarTopicsPage = lazy(() => import('./pages/GrammarTopicsPage'));
const PracticePage = lazy(() => import('./pages/PracticePage'));
const ProgressPage = lazy(() => import('./pages/ProgressPage'));

// Exercise pages
const ConversationPage = lazy(() => import('./pages/exercises/ConversationPage'));
const GrammarPage = lazy(() => import('./pages/exercises/GrammarPage'));
const TranslationPage = lazy(() => import('./pages/exercises/TranslationPage'));
const SentenceConstructionPage = lazy(() => import('./pages/exercises/SentenceConstructionPage'));
const ReadingPage = lazy(() => import('./pages/exercises/ReadingPage'));
const DialoguePage = lazy(() => import('./pages/exercises/DialoguePage'));

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <AppLayout>
        <Suspense fallback={<LoadingOverlay visible />}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/learn" element={<LearnPage />} />
            <Route path="/learn/conversation" element={<ConversationPage />} />
            <Route path="/learn/grammar" element={<GrammarPage />} />
            <Route path="/learn/translation" element={<TranslationPage />} />
            <Route path="/learn/sentence" element={<SentenceConstructionPage />} />
            <Route path="/learn/reading" element={<ReadingPage />} />
            <Route path="/learn/dialogue" element={<DialoguePage />} />
            <Route path="/vocabulary" element={<VocabularyPage />} />
            <Route path="/grammar" element={<GrammarTopicsPage />} />
            <Route path="/practice" element={<PracticePage />} />
            <Route path="/progress" element={<ProgressPage />} />
          </Routes>
        </Suspense>
      </AppLayout>
    </ErrorBoundary>
  );
};

export default App;
