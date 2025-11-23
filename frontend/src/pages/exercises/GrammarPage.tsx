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
  Loader,
  List,
} from '@mantine/core';
import { IconArrowLeft, IconCheck, IconX, IconRefresh } from '@tabler/icons-react';
import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { exerciseApi } from '~services/exerciseApi';
import type { CEFRLevel, GrammarExerciseResponse } from '~types';

const GrammarPage: React.FC = () => {
  const navigate = useNavigate();
  const [cefrLevel, setCefrLevel] = useState<CEFRLevel>('A1');
  const [exercise, setExercise] = useState<GrammarExerciseResponse & { expectedAnswer?: string } | null>(null);
  const [userAnswer, setUserAnswer] = useState('');
  const [result, setResult] = useState<{
    correct: boolean;
    feedback: string;
    explanation?: string | null;
  } | null>(null);
  const [exerciseStartTime, setExerciseStartTime] = useState<number | null>(null);

  // End chat session when leaving the page
  useEffect(() => {
    return () => {
      exerciseApi.endSession('grammar').catch(() => {});
    };
  }, []);

  const generateMutation = useMutation({
    mutationFn: () => exerciseApi.generateGrammar({}, cefrLevel),
    onSuccess: (data) => {
      setExercise(data);
      setUserAnswer('');
      setResult(null);
      setExerciseStartTime(Date.now());
    },
  });

  const evaluateMutation = useMutation({
    mutationFn: (answer: string) => {
      const durationMs = exerciseStartTime ? Date.now() - exerciseStartTime : 0;
      const durationMinutes = Math.max(1, Math.round(durationMs / 60000));
      return exerciseApi.evaluate({
        exercise_type: 'grammar',
        user_answer: answer,
        expected_answer: (exercise as any)?.expectedAnswer || '',
        context: exercise?.question || '',
        topic_id: exercise?.topic_id,  // Track progress for this grammar topic
        duration_minutes: durationMinutes,
      });
    },
    onSuccess: (data) => {
      setResult({
        correct: data.correct,
        feedback: data.feedback,
        explanation: data.explanation,
      });
    },
  });

  const handleSubmit = () => {
    if (!userAnswer.trim()) return;
    evaluateMutation.mutate(userAnswer);
  };

  const handleNext = () => {
    generateMutation.mutate();
  };

  // Handle Enter key for "Next Exercise" button when result is shown
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
            <Title order={2}>Grammar Exercises</Title>
            <Text c="dimmed" size="sm">
              Practice Croatian grammar
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
            <Text size="lg">Ready to practice grammar?</Text>
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
            <Badge color="green" size="lg">
              {exercise.topic_name}
            </Badge>

            <Paper p="md" bg="gray.0" radius="md">
              <Text fw={500} mb="xs">
                {exercise.instruction}
              </Text>
              <Text size="lg">{exercise.question}</Text>
            </Paper>

            {exercise.hints && exercise.hints.length > 0 && (
              <Alert color="blue" title="Hints">
                <List size="sm">
                  {exercise.hints.map((hint, i) => (
                    <List.Item key={i}>{hint}</List.Item>
                  ))}
                </List>
              </Alert>
            )}

            {!result ? (
              <>
                <TextInput
                  placeholder="Type your answer..."
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
                  Check Answer
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
                  {result.explanation && (
                    <Text size="sm" mt="xs" c="dimmed">
                      {result.explanation}
                    </Text>
                  )}
                </Alert>
                <Button
                  onClick={handleNext}
                  loading={generateMutation.isPending}
                  size="lg"
                  leftSection={<IconRefresh size={20} />}
                >
                  Next Exercise
                </Button>
              </>
            )}
          </Stack>
        </Card>
      )}
    </Stack>
  );
};

export default GrammarPage;
