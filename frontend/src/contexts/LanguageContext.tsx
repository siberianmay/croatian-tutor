import React, { createContext, useContext, useCallback, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { languageApi } from '~services/languageApi';
import type { Language, LanguageSetting } from '~types';

interface LanguageContextValue {
  /** Current language code (e.g., 'hr', 'it') */
  languageCode: string;
  /** Full language object with name, native_name, etc. */
  language: Language | null;
  /** All available languages for selection */
  availableLanguages: Language[];
  /** Whether data is still loading */
  isLoading: boolean;
  /** Change the current language */
  setLanguage: (code: string) => Promise<void>;
  /** Whether a language change is in progress */
  isChanging: boolean;
}

const LanguageContext = createContext<LanguageContextValue | null>(null);

interface LanguageProviderProps {
  children: React.ReactNode;
}

export const LanguageProvider: React.FC<LanguageProviderProps> = ({ children }) => {
  const queryClient = useQueryClient();

  // Fetch user's current language
  const { data: languageSetting, isLoading: isLoadingSetting } = useQuery({
    queryKey: ['userLanguage'],
    queryFn: languageApi.getUserLanguage,
  });

  // Fetch all available languages
  const { data: availableLanguages = [], isLoading: isLoadingLanguages } = useQuery({
    queryKey: ['languages'],
    queryFn: languageApi.getLanguages,
  });

  // Mutation to change language
  const mutation = useMutation({
    mutationFn: languageApi.setUserLanguage,
    onSuccess: (data: LanguageSetting) => {
      // Update the cached user language
      queryClient.setQueryData(['userLanguage'], data);
      // Invalidate queries that depend on language (vocabulary, topics, progress, etc.)
      queryClient.invalidateQueries({ queryKey: ['words'] });
      queryClient.invalidateQueries({ queryKey: ['topics'] });
      queryClient.invalidateQueries({ queryKey: ['progress'] });
      queryClient.invalidateQueries({ queryKey: ['analytics'] });
    },
  });

  const setLanguage = useCallback(async (code: string) => {
    await mutation.mutateAsync({ language_code: code });
  }, [mutation]);

  const value = useMemo<LanguageContextValue>(() => ({
    languageCode: languageSetting?.language_code ?? 'hr',
    language: languageSetting?.language ?? null,
    availableLanguages,
    isLoading: isLoadingSetting || isLoadingLanguages,
    setLanguage,
    isChanging: mutation.isPending,
  }), [
    languageSetting,
    availableLanguages,
    isLoadingSetting,
    isLoadingLanguages,
    setLanguage,
    mutation.isPending,
  ]);

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = (): LanguageContextValue => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};
