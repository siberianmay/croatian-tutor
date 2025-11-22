import React, { Suspense, lazy } from 'react';
import { Routes, Route } from 'react-router-dom';
import { LoadingOverlay } from '@mantine/core';

import { AppLayout } from '~components/layout/AppLayout';

const HomePage = lazy(() => import('./pages/HomePage'));
const LearnPage = lazy(() => import('./pages/LearnPage'));
const VocabularyPage = lazy(() => import('./pages/VocabularyPage'));
const PracticePage = lazy(() => import('./pages/PracticePage'));
const ProgressPage = lazy(() => import('./pages/ProgressPage'));

const App: React.FC = () => {
  return (
    <AppLayout>
      <Suspense fallback={<LoadingOverlay visible />}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/learn" element={<LearnPage />} />
          <Route path="/vocabulary" element={<VocabularyPage />} />
          <Route path="/practice" element={<PracticePage />} />
          <Route path="/progress" element={<ProgressPage />} />
        </Routes>
      </Suspense>
    </AppLayout>
  );
};

export default App;
