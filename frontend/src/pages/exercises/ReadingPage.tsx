import React, { useState, useEffect } from 'react';
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
  Divider,
  Progress,
} from '@mantine/core';
import { IconArrowLeft, IconCheck, IconX, IconRefresh, IconSend } from '@tabler/icons-react';
import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { exerciseApi } from '~services/exerciseApi';
import type { CEFRLevel, ReadingExerciseResponse, ReadingEvaluationResult } from '~types';

interface QuestionState {
  answer: string;
  result?: ReadingEvaluationResult | null;
}

const ReadingPage: React.FC = () => {
  const navigate = useNavigate();
  const [cefrLevel, setCefrLevel] = useState<CEFRLevel>('A1');
  const [exercise, setExercise] = useState<ReadingExerciseResponse | null>(null);
  const [questionStates, setQuestionStates] = useState<QuestionState[]>([]);
  const [submitted, setSubmitted] = useState(false);
  const [exerciseStartTime, setExerciseStartTime] = useState<number | null>(null);

  // End chat session when leaving the page
  useEffect(() => {
    return () => {
      exerciseApi.endSession('reading').catch(() => {});
    };
  }, []);

  const generateMutation = useMutation({
    mutationFn: () => exerciseApi.generateReading({ cefr_level: cefrLevel }),
    onSuccess: (data) => {
      setExercise(data);
      setQuestionStates(data.questions.map(() => ({ answer: '' })));
      setSubmitted(false);
      setExerciseStartTime(Date.now());
    },
  });

  const evaluateMutation = useMutation({
    mutationFn: async () => {
      if (!exercise) throw new Error('No exercise');
      const durationMs = exerciseStartTime ? Date.now() - exerciseStartTime : 0;
      const durationMinutes = Math.max(1, Math.round(durationMs / 60000));
      return exerciseApi.evaluateReadingBatch({
        passage: exercise.passage,
        answers: exercise.questions.map((q, idx) => ({
          question: q.question,
          expected_answer: q.expected_answer,
          user_answer: questionStates[idx]?.answer || '',
        })),
        duration_minutes: durationMinutes,
      });
    },
    onSuccess: (data) => {
      setQuestionStates((prev) =>
        prev.map((q, i) => ({
          ...q,
          result: data.results[i] || null,
        }))
      );
      setSubmitted(true);
    },
  });

  const handleAnswerChange = (index: number, answer: string) => {
    setQuestionStates((prev) =>
      prev.map((q, i) => (i === index ? { ...q, answer } : q))
    );
  };

  const handleSubmitAll = () => {
    if (!exercise) return;
    const hasAllAnswers = questionStates.every((q) => q.answer.trim());
    if (!hasAllAnswers) return;
    evaluateMutation.mutate();
  };

  // Calculate score summary
  const getScoreSummary = () => {
    if (!submitted) return null;
    const correct = questionStates.filter((q) => q.result?.correct).length;
    const total = questionStates.length;
    const percentage = Math.round((correct / total) * 100);
    return { correct, total, percentage };
  };

  const scoreSummary = getScoreSummary();
  const allAnswered = questionStates.length > 0 && questionStates.every((q) => q.answer.trim());

  // Handle Enter key for "Next Reading" button when submitted
  useEffect(() => {
    if (!submitted) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Enter' && !generateMutation.isPending) {
        generateMutation.mutate();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [submitted, generateMutation.isPending]);

  return (
    <Stack gap="lg">
      <Group justify="space-between">
        <Group>
          <ActionIcon variant="subtle" onClick={() => navigate('/')}>
            <IconArrowLeft size={20} />
          </ActionIcon>
          <div>
            <Title order={2}>Reading Comprehension</Title>
            <Text c="dimmed" size="sm">
              Read and answer questions
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

      {!exercise ? (
        <Card shadow="sm" padding="xl" radius="md" withBorder>
          <Stack align="center" gap="lg">
            <Text size="lg">Ready to practice reading?</Text>
            <Button
              size="lg"
              onClick={() => generateMutation.mutate()}
              loading={generateMutation.isPending}
              leftSection={<IconRefresh size={20} />}
            >
              Generate Reading Exercise
            </Button>
          </Stack>
        </Card>
      ) : (
        <Stack gap="lg">
          {/* Passage */}
          <Card shadow="sm" padding="xl" radius="md" withBorder>
            <Badge color="teal" mb="md">
              Reading Passage
            </Badge>
            <Paper p="lg" bg="gray.0" radius="md">
              <Text size="lg" style={{ lineHeight: 1.8 }}>
                {exercise.passage}
              </Text>
            </Paper>
          </Card>

          {/* Score Summary (shown after submission) */}
          {submitted && scoreSummary && (
            <Card shadow="sm" padding="lg" radius="md" withBorder>
              <Group justify="space-between" mb="md">
                <Title order={4}>Results</Title>
                <Badge
                  size="lg"
                  color={scoreSummary.percentage >= 70 ? 'green' : scoreSummary.percentage >= 50 ? 'yellow' : 'red'}
                >
                  {scoreSummary.correct}/{scoreSummary.total} correct ({scoreSummary.percentage}%)
                </Badge>
              </Group>
              <Progress
                value={scoreSummary.percentage}
                color={scoreSummary.percentage >= 70 ? 'green' : scoreSummary.percentage >= 50 ? 'yellow' : 'red'}
                size="lg"
                radius="md"
              />
            </Card>
          )}

          {/* Questions */}
          <Card shadow="sm" padding="xl" radius="md" withBorder>
            <Badge color="blue" mb="md">
              Comprehension Questions ({exercise.questions.length})
            </Badge>
            <Stack gap="lg">
              {exercise.questions.map((q, idx) => (
                <Paper key={idx} p="md" withBorder radius="md">
                  <Stack gap="md">
                    <Text fw={500}>
                      {idx + 1}. {q.question}
                    </Text>

                    <TextInput
                      placeholder="Your answer..."
                      value={questionStates[idx]?.answer || ''}
                      onChange={(e) => handleAnswerChange(idx, e.target.value)}
                      disabled={submitted}
                    />

                    {questionStates[idx]?.result && (
                      <Alert
                        icon={
                          questionStates[idx].result?.correct ? (
                            <IconCheck size={16} />
                          ) : (
                            <IconX size={16} />
                          )
                        }
                        color={questionStates[idx].result?.correct ? 'green' : 'red'}
                      >
                        <Text size="sm">{questionStates[idx].result?.feedback}</Text>
                      </Alert>
                    )}
                  </Stack>
                </Paper>
              ))}

              <Divider />

              {!submitted ? (
                <Button
                  onClick={handleSubmitAll}
                  loading={evaluateMutation.isPending}
                  size="lg"
                  leftSection={<IconSend size={20} />}
                  disabled={!allAnswered}
                >
                  Submit All Answers
                </Button>
              ) : (
                <Button
                  onClick={() => generateMutation.mutate()}
                  loading={generateMutation.isPending}
                  size="lg"
                  leftSection={<IconRefresh size={20} />}
                >
                  Next Reading
                </Button>
              )}
            </Stack>
          </Card>
        </Stack>
      )}
    </Stack>
  );
};

export default ReadingPage;
