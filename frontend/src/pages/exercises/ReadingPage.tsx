import React, { useState } from 'react';
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
} from '@mantine/core';
import { IconArrowLeft, IconCheck, IconX, IconRefresh } from '@tabler/icons-react';
import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { exerciseApi } from '~services/exerciseApi';
import type { CEFRLevel, ReadingExerciseResponse } from '~types';

interface QuestionState {
  answer: string;
  result?: { correct: boolean; feedback: string } | null;
}

const ReadingPage: React.FC = () => {
  const navigate = useNavigate();
  const [cefrLevel, setCefrLevel] = useState<CEFRLevel>('A1');
  const [exercise, setExercise] = useState<ReadingExerciseResponse | null>(null);
  const [questionStates, setQuestionStates] = useState<QuestionState[]>([]);
  const [allAnswered, setAllAnswered] = useState(false);

  const generateMutation = useMutation({
    mutationFn: () => exerciseApi.generateReading({ cefr_level: cefrLevel }),
    onSuccess: (data) => {
      setExercise(data);
      setQuestionStates(data.questions.map(() => ({ answer: '' })));
      setAllAnswered(false);
    },
  });

  const evaluateMutation = useMutation({
    mutationFn: async ({ index, answer, expected }: { index: number; answer: string; expected: string }) => {
      const result = await exerciseApi.evaluate({
        exercise_type: 'reading',
        user_answer: answer,
        expected_answer: expected,
        context: exercise?.passage || '',
      });
      return { index, result };
    },
    onSuccess: ({ index, result }) => {
      setQuestionStates((prev) =>
        prev.map((q, i) =>
          i === index ? { ...q, result: { correct: result.correct, feedback: result.feedback } } : q
        )
      );
      // Check if all questions answered
      setAllAnswered(true);
    },
  });

  const handleAnswerChange = (index: number, answer: string) => {
    setQuestionStates((prev) =>
      prev.map((q, i) => (i === index ? { ...q, answer } : q))
    );
  };

  const handleCheckAnswer = (index: number) => {
    if (!exercise) return;
    const state = questionStates[index];
    if (!state?.answer.trim()) return;

    evaluateMutation.mutate({
      index,
      answer: state.answer,
      expected: exercise.questions[index].expected_answer,
    });
  };

  return (
    <Stack gap="lg">
      <Group justify="space-between">
        <Group>
          <ActionIcon variant="subtle" onClick={() => navigate('/learn')}>
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

          {/* Questions */}
          <Card shadow="sm" padding="xl" radius="md" withBorder>
            <Badge color="blue" mb="md">
              Comprehension Questions
            </Badge>
            <Stack gap="lg">
              {exercise.questions.map((q, idx) => (
                <Paper key={idx} p="md" withBorder radius="md">
                  <Stack gap="md">
                    <Text fw={500}>
                      {idx + 1}. {q.question}
                    </Text>

                    {!questionStates[idx]?.result ? (
                      <Group>
                        <TextInput
                          placeholder="Your answer..."
                          value={questionStates[idx]?.answer || ''}
                          onChange={(e) => handleAnswerChange(idx, e.target.value)}
                          flex={1}
                          onKeyPress={(e) => e.key === 'Enter' && handleCheckAnswer(idx)}
                        />
                        <Button
                          onClick={() => handleCheckAnswer(idx)}
                          loading={evaluateMutation.isPending}
                          disabled={!questionStates[idx]?.answer?.trim()}
                        >
                          Check
                        </Button>
                      </Group>
                    ) : (
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

              {allAnswered && (
                <>
                  <Divider />
                  <Button
                    onClick={() => generateMutation.mutate()}
                    loading={generateMutation.isPending}
                    size="lg"
                    leftSection={<IconRefresh size={20} />}
                  >
                    Next Reading
                  </Button>
                </>
              )}
            </Stack>
          </Card>
        </Stack>
      )}
    </Stack>
  );
};

export default ReadingPage;
