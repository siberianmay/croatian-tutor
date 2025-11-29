import React, { useState, useEffect } from 'react';
import {
  Title,
  Text,
  Stack,
  Card,
  Button,
  Group,
  NumberInput,
  Select,
  Slider,
  Alert,
  Loader,
  Divider,
  Badge,
  SimpleGrid,
} from '@mantine/core';
import { IconSettings, IconCheck, IconAlertCircle, IconRefresh, IconLanguage } from '@tabler/icons-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { settingsApi } from '~services/settingsApi';
import { useLanguage } from '~contexts/LanguageContext';
import type { AppSettings, AppSettingsUpdate, GeminiModel } from '~types';

const GEMINI_MODELS: { value: GeminiModel; label: string }[] = [
  { value: 'gemini-2.0-flash', label: 'Gemini 2.0 Flash' },
  { value: 'gemini-2.0-flash-lite', label: 'Gemini 2.0 Flash Lite' },
  { value: 'gemini-2.5-flash-lite', label: 'Gemini 2.5 Flash Lite' },
  { value: 'gemini-2.5-flash', label: 'Gemini 2.5 Flash (Recommended)' },
  { value: 'gemini-2.5-pro', label: 'Gemini 2.5 Pro (Best Quality)' },
];

const DEFAULT_SETTINGS: AppSettingsUpdate = {
  grammar_batch_size: 10,
  translation_batch_size: 10,
  reading_passage_length: 350,
  gemini_model: 'gemini-2.5-flash',
};

const SettingsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [formValues, setFormValues] = useState<AppSettingsUpdate>({});
  const [hasChanges, setHasChanges] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [languageSuccess, setLanguageSuccess] = useState(false);

  const {
    languageCode,
    language,
    availableLanguages,
    setLanguage,
    isChanging: isLanguageChanging,
  } = useLanguage();

  const { data: settings, isLoading, error } = useQuery({
    queryKey: ['settings'],
    queryFn: settingsApi.get,
  });

  const mutation = useMutation({
    mutationFn: settingsApi.update,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] });
      setHasChanges(false);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    },
  });

  // Initialize form values when settings load
  useEffect(() => {
    if (settings) {
      setFormValues({
        grammar_batch_size: settings.grammar_batch_size,
        translation_batch_size: settings.translation_batch_size,
        reading_passage_length: settings.reading_passage_length,
        gemini_model: settings.gemini_model,
      });
    }
  }, [settings]);

  const handleChange = <K extends keyof AppSettingsUpdate>(
    field: K,
    value: AppSettingsUpdate[K]
  ) => {
    setFormValues((prev) => ({ ...prev, [field]: value }));
    setHasChanges(true);
    setSaveSuccess(false);
  };

  const handleSave = () => {
    mutation.mutate(formValues);
  };

  const handleReset = () => {
    setFormValues(DEFAULT_SETTINGS);
    setHasChanges(true);
    setSaveSuccess(false);
  };

  const handleLanguageChange = async (code: string | null) => {
    if (!code) return;
    try {
      await setLanguage(code);
      setLanguageSuccess(true);
      setTimeout(() => setLanguageSuccess(false), 3000);
    } catch (err) {
      console.error('Failed to change language:', err);
    }
  };

  if (isLoading) {
    return (
      <Stack gap="lg" align="center" mt="xl">
        <Loader size="lg" />
        <Text c="dimmed">Loading settings...</Text>
      </Stack>
    );
  }

  if (error) {
    return (
      <Alert color="red" title="Error loading settings" icon={<IconAlertCircle />}>
        Failed to load application settings. Please try refreshing the page.
      </Alert>
    );
  }

  return (
    <Stack gap="lg">
      <Group justify="space-between" align="flex-start">
        <div>
          <Title order={1}>Settings</Title>
          <Text c="dimmed" mt="sm">
            Configure exercise generation and AI model settings
          </Text>
        </div>
        {settings && (
          <Badge color="gray" size="sm">
            Last updated: {new Date(settings.updated_at).toLocaleString()}
          </Badge>
        )}
      </Group>

      {saveSuccess && (
        <Alert color="green" icon={<IconCheck />} title="Settings saved">
          Your settings have been saved successfully.
        </Alert>
      )}

      {mutation.isError && (
        <Alert color="red" icon={<IconAlertCircle />} title="Error saving settings">
          Failed to save settings. Please try again.
        </Alert>
      )}

      {languageSuccess && (
        <Alert color="green" icon={<IconCheck />} title="Language changed">
          Your learning language has been changed to {language?.name}.
        </Alert>
      )}

      <Card shadow="sm" padding="lg" withBorder>
        <Stack gap="md">
          <Group gap="xs">
            <IconLanguage size={20} />
            <Text fw={600} size="lg">Learning Language</Text>
          </Group>
          <Text size="sm" c="dimmed">
            Select the language you want to learn. Your vocabulary, exercises, and progress
            are tracked separately for each language.
          </Text>
          <Divider />

          <Select
            label="Language"
            description="Choose your target learning language"
            data={availableLanguages.map((lang) => ({
              value: lang.code,
              label: `${lang.name} (${lang.native_name})`,
            }))}
            value={languageCode}
            onChange={handleLanguageChange}
            allowDeselect={false}
            disabled={isLanguageChanging}
            rightSection={isLanguageChanging ? <Loader size="xs" /> : undefined}
          />
        </Stack>
      </Card>

      <Card shadow="sm" padding="lg" withBorder>
        <Stack gap="md">
          <Group gap="xs">
            <IconSettings size={20} />
            <Text fw={600} size="lg">Exercise Batch Sizes</Text>
          </Group>
          <Text size="sm" c="dimmed">
            Control how many exercises are generated in each batch request.
          </Text>
          <Divider />

          <SimpleGrid cols={{ base: 1, sm: 2 }}>
            <NumberInput
              label="Grammar Batch Size"
              description="Exercises per request (3-20)"
              value={formValues.grammar_batch_size}
              onChange={(val) => handleChange('grammar_batch_size', val as number)}
              min={3}
              max={20}
              step={1}
            />

            <NumberInput
              label="Translation Batch Size"
              description="Exercises per request (3-20)"
              value={formValues.translation_batch_size}
              onChange={(val) => handleChange('translation_batch_size', val as number)}
              min={3}
              max={20}
              step={1}
            />
          </SimpleGrid>
        </Stack>
      </Card>

      <Card shadow="sm" padding="lg" withBorder>
        <Stack gap="md">
          <Text fw={600} size="lg">Reading Comprehension</Text>
          <Text size="sm" c="dimmed">
            Configure the length of reading passages.
          </Text>
          <Divider />

          <div>
            <Text size="sm" fw={500} mb="xs">
              Passage Length: {formValues.reading_passage_length} characters
            </Text>
            <Text size="xs" c="dimmed" mb="md">
              Approximate length of reading passages (100-1000 characters)
            </Text>
            <Slider
              value={formValues.reading_passage_length}
              onChange={(val) => handleChange('reading_passage_length', val)}
              min={100}
              max={1000}
              step={50}
              marks={[
                { value: 100, label: 'Short' },
                { value: 350, label: 'Medium' },
                { value: 700, label: 'Long' },
                { value: 1000, label: 'Very Long' },
              ]}
            />
          </div>
        </Stack>
      </Card>

      <Card shadow="sm" padding="lg" withBorder>
        <Stack gap="md">
          <Text fw={600} size="lg">AI Model</Text>
          <Text size="sm" c="dimmed">
            Select the Gemini model used for generating exercises and evaluating answers.
          </Text>
          <Divider />

          <Select
            label="Gemini Model"
            description="Higher-tier models produce better quality but may be slower"
            data={GEMINI_MODELS}
            value={formValues.gemini_model}
            onChange={(val) => handleChange('gemini_model', val as GeminiModel)}
            allowDeselect={false}
          />
        </Stack>
      </Card>

      <Group justify="space-between">
        <Button
          variant="subtle"
          color="gray"
          leftSection={<IconRefresh size={16} />}
          onClick={handleReset}
        >
          Reset to Defaults
        </Button>

        <Button
          onClick={handleSave}
          loading={mutation.isPending}
          disabled={!hasChanges}
          leftSection={<IconCheck size={16} />}
        >
          Save Settings
        </Button>
      </Group>
    </Stack>
  );
};

export default SettingsPage;
