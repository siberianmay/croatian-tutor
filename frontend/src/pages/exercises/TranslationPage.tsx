import React, { useState, useEffect, useRef } from 'react';
import {
  Title,
  Text,
  Stack,
  Card,
  TextInput,
  Button,
  Paper,
  Group,
  Badge,
  Alert,
  Select,
  ActionIcon,
  SegmentedControl,
} from '@mantine/core';
import { IconArrowLeft, IconCheck, IconX, IconRefresh, IconArrowRight } from '@tabler/icons-react';
import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { exerciseApi } from '~services/exerciseApi';
import type { CEFRLevel, TranslationResponse } from '~types';

type Direction = 'cr_en' | 'en_cr';

const TranslationPage: React.FC = () => {
  const navigate = useNavigate();
  const [cefrLevel, setCefrLevel] = useState<CEFRLevel>('A1');
  const [direction, setDirection] = useState<Direction>('en_cr');
  const [exercise, setExercise] = useState<TranslationResponse | null>(null);
  const [userAnswer, setUserAnswer] = useState('');
  const [result, setResult] = useState<{
    correct: boolean;
    feedback: string;
    correctAnswer?: string | null;
  } | null>(null);
  const [exerciseStartTime, setExerciseStartTime] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // End chat session when leaving the page
  useEffect(() => {
    return () => {
      // End session for the current direction on unmount
      exerciseApi.endSession('translation', direction).catch(() => {
        // Silently ignore errors on cleanup
      });
    };
  }, [direction]);

  const generateMutation = useMutation({
    mutationFn: () =>
      exerciseApi.generateTranslation({
        direction,
        cefr_level: cefrLevel,
      }),
    onSuccess: (data) => {
      setExercise(data);
      setUserAnswer('');
      setResult(null);
      setError(null);
      setExerciseStartTime(Date.now());
      // Focus input after render
      setTimeout(() => inputRef.current?.focus(), 0);
    },
    onError: (err: Error & { response?: { data?: { message?: string; detail?: string } } }) => {
      const message = err.response?.data?.message || err.response?.data?.detail || err.message || 'Failed to generate exercise';
      setError(message);
    },
  });

  const evaluateMutation = useMutation({
    mutationFn: (answer: string) => {
      const durationMs = exerciseStartTime ? Date.now() - exerciseStartTime : 0;
      const durationMinutes = Math.max(1, Math.round(durationMs / 60000));
      return exerciseApi.evaluate({
        exercise_type: direction === 'cr_en' ? 'translation_cr_en' : 'translation_en_cr',
        user_answer: answer,
        expected_answer: exercise?.expected_answer || '',
        context: `Translate: ${exercise?.source_text}`,
        topic_id: exercise?.topic_id ?? undefined,
        duration_minutes: durationMinutes,
      });
    },
    onSuccess: (data) => {
      setResult({
        correct: data.correct,
        feedback: data.feedback,
        correctAnswer: data.correct_answer,
      });
    },
  });

  const handleSubmit = () => {
    if (!userAnswer.trim()) return;
    evaluateMutation.mutate(userAnswer);
  };

  // Handle Enter key for "Next Translation" button when result is shown
  useEffect(() => {
    if (!result) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Enter' && !generateMutation.isPending) {
        generateMutation.mutate();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [result, generateMutation.isPending]);

  return (
    <Stack gap="lg">
      <Group justify="space-between">
        <Group>
          <ActionIcon variant="subtle" onClick={() => navigate('/')}>
            <IconArrowLeft size={20} />
          </ActionIcon>
          <div>
            <Title order={2}>Translation</Title>
            <Text c="dimmed" size="sm">
              Translate between Croatian and English
            </Text>
          </div>
        </Group>
        <Select
          value={cefrLevel}
          onChange={(v) => setCefrLevel((v || 'A1') as CEFRLevel)}
          data={['A1', 'A2', 'B1', 'B2', 'C1', 'C2']}
          w={100}
          size="sm"
        />
      </Group>

      {error && (
        <Alert color="red" title="Error" icon={<IconX size={20} />} withCloseButton onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {!exercise ? (
        <Card shadow="sm" padding="xl" radius="md" withBorder>
          <Stack align="center" gap="lg">
            <Text size="lg">Choose translation direction:</Text>
            <SegmentedControl
              value={direction}
              onChange={(v) => setDirection(v as Direction)}
              data={[
                { label: 'Croatian → English', value: 'cr_en' },
                { label: 'English → Croatian', value: 'en_cr' },
              ]}
              size="md"
            />
            <Button
              size="lg"
              onClick={() => generateMutation.mutate()}
              loading={generateMutation.isPending}
              leftSection={<IconRefresh size={20} />}
            >
              Generate Exercise
            </Button>
          </Stack>
        </Card>
      ) : (
        <Card shadow="sm" padding="xl" radius="md" withBorder>
          <Stack gap="lg">
            <Group justify="center">
              <Badge color="orange" size="lg">
                {exercise.source_language}
              </Badge>
              <IconArrowRight size={20} />
              <Badge color="blue" size="lg">
                {exercise.target_language}
              </Badge>
            </Group>

            {exercise.topic_name && (
              <Badge color="green" size="sm" variant="light">
                Grammar: {exercise.topic_name}
              </Badge>
            )}

            <Paper p="xl" bg="gray.0" radius="md" ta="center">
              <Text size="xl" fw={500}>
                {exercise.source_text}
              </Text>
            </Paper>

            {!result ? (
              <>
                <TextInput
                  ref={inputRef}
                  placeholder={`Translate to ${exercise.target_language}...`}
                  value={userAnswer}
                  onChange={(e) => setUserAnswer(e.target.value)}
                  size="lg"
                  onKeyPress={(e) => e.key === 'Enter' && handleSubmit()}
                />
                <Button
                  onClick={handleSubmit}
                  loading={evaluateMutation.isPending}
                  disabled={!userAnswer.trim()}
                  size="lg"
                >
                  Check Translation
                </Button>
              </>
            ) : (
              <>
                <Alert
                  icon={result.correct ? <IconCheck size={20} /> : <IconX size={20} />}
                  color={result.correct ? 'green' : 'red'}
                  title={result.correct ? 'Correct!' : 'Incorrect'}
                >
                  <Text>{result.feedback}</Text>
                  {result.correctAnswer && (
                    <Text size="sm" mt="xs" fw={500}>
                      Expected: {result.correctAnswer}
                    </Text>
                  )}
                </Alert>
                <Button
                  onClick={() => generateMutation.mutate()}
                  loading={generateMutation.isPending}
                  size="lg"
                  leftSection={<IconRefresh size={20} />}
                >
                  Next Translation
                </Button>
              </>
            )}
          </Stack>
        </Card>
      )}
    </Stack>
  );
};

export default TranslationPage;
