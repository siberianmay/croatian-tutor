import React, { useState, useEffect, useRef, useCallback } from 'react';
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
  Progress,
  Divider,
  List,
  ThemeIcon,
} from '@mantine/core';
import { IconArrowLeft, IconCheck, IconX, IconRefresh, IconArrowRight, IconPlayerPlay } from '@tabler/icons-react';
import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { exerciseApi } from '~services/exerciseApi';
import type { CEFRLevel, TranslationBatchItem, TranslationEvaluationResult, TranslationAnswerItem } from '~types';

type Direction = 'cr_en' | 'en_cr';

interface UserAnswer {
  exercise: TranslationBatchItem;
  userAnswer: string;
}

const TranslationPage: React.FC = () => {
  const navigate = useNavigate();
  const [cefrLevel, setCefrLevel] = useState<CEFRLevel>('A1');
  const [direction, setDirection] = useState<Direction>('en_cr');

  // Batch state
  const [exercises, setExercises] = useState<TranslationBatchItem[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState<UserAnswer[]>([]);
  const [currentAnswer, setCurrentAnswer] = useState('');

  // Results state
  const [results, setResults] = useState<TranslationEvaluationResult[] | null>(null);
  const [showResults, setShowResults] = useState(false);

  // Timing
  const [sessionStartTime, setSessionStartTime] = useState<number | null>(null);

  // UI state
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const currentExercise = exercises[currentIndex] || null;
  const isLastExercise = currentIndex === exercises.length - 1;
  const progress = exercises.length > 0 ? ((currentIndex + 1) / exercises.length) * 100 : 0;

  // Generate batch mutation
  const generateBatchMutation = useMutation({
    mutationFn: () =>
      exerciseApi.generateTranslationBatch({
        direction,
        cefr_level: cefrLevel,
      }),
    onSuccess: (data) => {
      setExercises(data.exercises);
      setCurrentIndex(0);
      setUserAnswers([]);
      setCurrentAnswer('');
      setResults(null);
      setShowResults(false);
      setError(null);
      setSessionStartTime(Date.now());
      setTimeout(() => inputRef.current?.focus(), 0);
    },
    onError: (err: Error & { response?: { data?: { message?: string; detail?: string } } }) => {
      const message = err.response?.data?.message || err.response?.data?.detail || err.message || 'Failed to generate exercises';
      setError(message);
    },
  });

  // Evaluate batch mutation
  const evaluateBatchMutation = useMutation({
    mutationFn: (answers: TranslationAnswerItem[]) => {
      const durationMs = sessionStartTime ? Date.now() - sessionStartTime : 0;
      const durationMinutes = Math.max(1, Math.round(durationMs / 60000));
      return exerciseApi.evaluateTranslationBatch({
        answers,
        duration_minutes: durationMinutes,
      });
    },
    onSuccess: (data) => {
      setResults(data.results);
      setShowResults(true);
    },
    onError: (err: Error & { response?: { data?: { message?: string; detail?: string } } }) => {
      const message = err.response?.data?.message || err.response?.data?.detail || err.message || 'Failed to evaluate answers';
      setError(message);
    },
  });

  // Handle submitting current answer and moving to next
  const handleSubmitAnswer = useCallback(() => {
    if (!currentAnswer.trim() || !currentExercise) return;

    const newAnswer: UserAnswer = {
      exercise: currentExercise,
      userAnswer: currentAnswer.trim(),
    };

    const updatedAnswers = [...userAnswers, newAnswer];
    setUserAnswers(updatedAnswers);
    setCurrentAnswer('');

    if (isLastExercise) {
      // Submit all for evaluation
      const answersForEval: TranslationAnswerItem[] = updatedAnswers.map((a) => ({
        user_answer: a.userAnswer,
        expected_answer: a.exercise.expected_answer,
        source_text: a.exercise.source_text,
        topic_id: a.exercise.topic_id,
      }));
      evaluateBatchMutation.mutate(answersForEval);
    } else {
      // Move to next exercise
      setCurrentIndex((prev) => prev + 1);
      setTimeout(() => inputRef.current?.focus(), 0);
    }
  }, [currentAnswer, currentExercise, isLastExercise, userAnswers, evaluateBatchMutation]);

  // Handle Enter key
  useEffect(() => {
    if (showResults) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Enter' && currentAnswer.trim() && !evaluateBatchMutation.isPending) {
        handleSubmitAnswer();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [currentAnswer, handleSubmitAnswer, evaluateBatchMutation.isPending, showResults]);

  // Handle Enter to start new batch from results
  useEffect(() => {
    if (!showResults) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Enter' && !generateBatchMutation.isPending) {
        generateBatchMutation.mutate();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [showResults, generateBatchMutation]);

  // Calculate summary stats
  const getSummaryStats = () => {
    if (!results) return { correct: 0, total: 0, score: 0 };
    const correct = results.filter((r) => r.correct).length;
    const total = results.length;
    const score = total > 0 ? Math.round((correct / total) * 100) : 0;
    return { correct, total, score };
  };

  const stats = getSummaryStats();

  // Render start screen
  if (exercises.length === 0 && !showResults) {
    return (
      <Stack gap="lg">
        <Group justify="space-between">
          <Group>
            <ActionIcon variant="subtle" onClick={() => navigate('/')}>
              <IconArrowLeft size={20} />
            </ActionIcon>
            <div>
              <Title order={2}>Translation (Batch Mode)</Title>
              <Text c="dimmed" size="sm">
                Complete translations, then get all results at once
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
            <Text size="sm" c="dimmed" ta="center">
              You'll get sentences to translate.<br />
              Complete all, then see your results.
            </Text>
            <Button
              size="lg"
              onClick={() => generateBatchMutation.mutate()}
              loading={generateBatchMutation.isPending}
              leftSection={<IconPlayerPlay size={20} />}
            >
              Start Session
            </Button>
          </Stack>
        </Card>
      </Stack>
    );
  }

  // Render results screen
  if (showResults && results) {
    return (
      <Stack gap="lg">
        <Group justify="space-between">
          <Group>
            <ActionIcon variant="subtle" onClick={() => navigate('/')}>
              <IconArrowLeft size={20} />
            </ActionIcon>
            <div>
              <Title order={2}>Session Results</Title>
              <Text c="dimmed" size="sm">
                {stats.correct} of {stats.total} correct ({stats.score}%)
              </Text>
            </div>
          </Group>
        </Group>

        <Card shadow="sm" padding="lg" radius="md" withBorder>
          <Stack gap="md">
            <Group justify="center">
              <Badge size="xl" color={stats.score >= 70 ? 'green' : stats.score >= 50 ? 'yellow' : 'red'}>
                Score: {stats.score}%
              </Badge>
            </Group>

            <Progress value={stats.score} color={stats.score >= 70 ? 'green' : stats.score >= 50 ? 'yellow' : 'red'} size="lg" />

            <Divider label="Details" labelPosition="center" />

            <List spacing="md" size="sm">
              {userAnswers.map((answer, idx) => {
                const result = results[idx];
                return (
                  <List.Item
                    key={idx}
                    icon={
                      <ThemeIcon color={result?.correct ? 'green' : 'red'} size={24} radius="xl">
                        {result?.correct ? <IconCheck size={16} /> : <IconX size={16} />}
                      </ThemeIcon>
                    }
                  >
                    <Text size="sm" fw={500}>{answer.exercise.source_text}</Text>
                    <Text size="xs" c="dimmed">
                      Your answer: <Text span c={result?.correct ? 'green' : 'red'}>{answer.userAnswer}</Text>
                    </Text>
                    {!result?.correct && (
                      <Text size="xs" c="dimmed">
                        Expected: <Text span fw={500}>{answer.exercise.expected_answer}</Text>
                      </Text>
                    )}
                    {result?.feedback && (
                      <Text size="xs" c="dimmed" fs="italic">{result.feedback}</Text>
                    )}
                  </List.Item>
                );
              })}
            </List>

            <Divider />

            <Button
              size="lg"
              onClick={() => generateBatchMutation.mutate()}
              loading={generateBatchMutation.isPending}
              leftSection={<IconRefresh size={20} />}
              fullWidth
            >
              Start New Session
            </Button>
          </Stack>
        </Card>
      </Stack>
    );
  }

  // Render exercise screen
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
              Exercise {currentIndex + 1} of {exercises.length}
            </Text>
          </div>
        </Group>
        <Badge size="lg" variant="light">
          {cefrLevel}
        </Badge>
      </Group>

      <Progress value={progress} size="sm" />

      {error && (
        <Alert color="red" title="Error" icon={<IconX size={20} />} withCloseButton onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {currentExercise && (
        <Card shadow="sm" padding="xl" radius="md" withBorder>
          <Stack gap="lg">
            <Group justify="center">
              <Badge color="orange" size="lg">
                {currentExercise.source_language}
              </Badge>
              <IconArrowRight size={20} />
              <Badge color="blue" size="lg">
                {currentExercise.target_language}
              </Badge>
            </Group>

            {currentExercise.topic_name && (
              <Badge color="green" size="sm" variant="light" style={{ alignSelf: 'center' }}>
                Grammar: {currentExercise.topic_name}
              </Badge>
            )}

            <Paper p="xl" bg="gray.0" radius="md" ta="center">
              <Text size="xl" fw={500}>
                {currentExercise.source_text}
              </Text>
            </Paper>

            <TextInput
              ref={inputRef}
              placeholder={`Translate to ${currentExercise.target_language}...`}
              value={currentAnswer}
              onChange={(e) => setCurrentAnswer(e.target.value)}
              size="lg"
            />

            <Button
              onClick={handleSubmitAnswer}
              loading={evaluateBatchMutation.isPending}
              disabled={!currentAnswer.trim()}
              size="lg"
              rightSection={isLastExercise ? <IconCheck size={20} /> : <IconArrowRight size={20} />}
            >
              {isLastExercise ? 'Submit All Answers' : 'Next'}
            </Button>

            <Text size="xs" c="dimmed" ta="center">
              Press Enter to continue • {exercises.length - currentIndex - 1} remaining
            </Text>
          </Stack>
        </Card>
      )}
    </Stack>
  );
};

export default TranslationPage;
