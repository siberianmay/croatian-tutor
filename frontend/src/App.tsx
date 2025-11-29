import React, { Suspense, lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { LoadingOverlay } from '@mantine/core';

import { AppLayout } from '~components/layout/AppLayout';
import ErrorBoundary from '~components/ErrorBoundary';
import { useAuth } from '~contexts/AuthContext';
import { LanguageProvider } from '~contexts/LanguageContext';

const LoginPage = lazy(() => import('./pages/LoginPage'));
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
const SettingsPage = lazy(() => import('./pages/SettingsPage'));

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingOverlay visible />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

const App: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingOverlay visible />;
  }

  return (
    <ErrorBoundary>
      <Suspense fallback={<LoadingOverlay visible />}>
        <Routes>
          {/* Public route */}
          <Route
            path="/login"
            element={
              isAuthenticated ? <Navigate to="/" replace /> : <LoginPage />
            }
          />

          {/* Protected routes */}
          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <LanguageProvider>
                  <AppLayout>
                    <Suspense fallback={<LoadingOverlay visible />}>
                      <Routes>
                        <Route path="/" element={<LearnPage />} />
                        <Route path="/conversation" element={<ConversationPage />} />
                        <Route path="/grammar-exercises" element={<GrammarPage />} />
                        <Route path="/translation" element={<TranslationPage />} />
                        <Route path="/sentence" element={<SentenceConstructionPage />} />
                        <Route path="/reading" element={<ReadingPage />} />
                        <Route path="/dialogue" element={<DialoguePage />} />
                        <Route path="/vocabulary" element={<VocabularyPage />} />
                        <Route path="/grammar" element={<GrammarTopicsPage />} />
                        <Route path="/flashcards" element={<PracticePage />} />
                        <Route path="/progress" element={<ProgressPage />} />
                        <Route path="/settings" element={<SettingsPage />} />
                      </Routes>
                    </Suspense>
                  </AppLayout>
                </LanguageProvider>
              </ProtectedRoute>
            }
          />
        </Routes>
      </Suspense>
    </ErrorBoundary>
  );
};

export default App;
