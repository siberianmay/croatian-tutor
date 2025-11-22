import React, { useState, useMemo } from 'react';
import {
  Title,
  Text,
  Stack,
  Card,
  Button,
  Paper,
  Group,
  Badge,
  Alert,
  Select,
  ActionIcon,
} from '@mantine/core';
import { IconArrowLeft, IconCheck, IconX, IconRefresh } from '@tabler/icons-react';
import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { exerciseApi } from '~services/exerciseApi';
import type { CEFRLevel, SentenceConstructionResponse } from '~types';

const SentenceConstructionPage: React.FC = () => {
  const navigate = useNavigate();
  const [cefrLevel, setCefrLevel] = useState<CEFRLevel>('A1');
  const [exercise, setExercise] = useState<SentenceConstructionResponse & { expectedAnswer?: string } | null>(null);
  const [selectedWords, setSelectedWords] = useState<string[]>([]);
  const [result, setResult] = useState<{
    correct: boolean;
    feedback: string;
    correctAnswer?: string | null;
  } | null>(null);

  const availableWords = useMemo(() => {
    if (!exercise) return [];
    return exercise.words.filter((w) => !selectedWords.includes(w));
  }, [exercise, selectedWords]);

  const generateMutation = useMutation({
    mutationFn: () => exerciseApi.generateSentenceConstruction({ cefr_level: cefrLevel }),
    onSuccess: (data) => {
      setExercise(data);
      setSelectedWords([]);
      setResult(null);
    },
  });

  const evaluateMutation = useMutation({
    mutationFn: (answer: string) =>
      exerciseApi.evaluate({
        exercise_type: 'sentence_construction',
        user_answer: answer,
        expected_answer: (exercise as any)?.expectedAnswer || '',
        context: exercise?.hint || '',
      }),
    onSuccess: (data) => {
      setResult({
        correct: data.correct,
        feedback: data.feedback,
        correctAnswer: data.correct_answer,
      });
    },
  });

  const handleWordClick = (word: string) => {
    setSelectedWords((prev) => [...prev, word]);
  };

  const handleRemoveWord = (index: number) => {
    setSelectedWords((prev) => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = () => {
    if (selectedWords.length === 0) return;
    evaluateMutation.mutate(selectedWords.join(' '));
  };

  const handleReset = () => {
    setSelectedWords([]);
    setResult(null);
  };

  return (
    <Stack gap="lg">
      <Group justify="space-between">
        <Group>
          <ActionIcon variant="subtle" onClick={() => navigate('/learn')}>
            <IconArrowLeft size={20} />
          </ActionIcon>
          <div>
            <Title order={2}>Sentence Construction</Title>
            <Text c="dimmed" size="sm">
              Arrange words to form correct sentences
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
            <Text size="lg">Ready to build sentences?</Text>
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
            <Alert color="blue">
              <Text fw={500}>Hint: {exercise.hint}</Text>
            </Alert>

            {/* Selected words (sentence being built) */}
            <Paper p="md" bg="gray.0" radius="md" mih={60}>
              <Text size="sm" c="dimmed" mb="xs">
                Your sentence:
              </Text>
              <Group gap="xs">
                {selectedWords.length === 0 ? (
                  <Text c="dimmed" fs="italic">
                    Click words below to build your sentence
                  </Text>
                ) : (
                  selectedWords.map((word, idx) => (
                    <Badge
                      key={idx}
                      size="lg"
                      color="blue"
                      style={{ cursor: 'pointer' }}
                      onClick={() => handleRemoveWord(idx)}
                    >
                      {word} ×
                    </Badge>
                  ))
                )}
              </Group>
            </Paper>

            {/* Available words */}
            {!result && (
              <Paper p="md" withBorder radius="md">
                <Text size="sm" c="dimmed" mb="xs">
                  Available words:
                </Text>
                <Group gap="xs">
                  {availableWords.map((word, idx) => (
                    <Badge
                      key={idx}
                      size="lg"
                      color="gray"
                      variant="outline"
                      style={{ cursor: 'pointer' }}
                      onClick={() => handleWordClick(word)}
                    >
                      {word}
                    </Badge>
                  ))}
                </Group>
              </Paper>
            )}

            {!result ? (
              <Group>
                <Button variant="outline" onClick={handleReset} disabled={selectedWords.length === 0}>
                  Reset
                </Button>
                <Button
                  onClick={handleSubmit}
                  loading={evaluateMutation.isPending}
                  disabled={selectedWords.length === 0}
                  flex={1}
                >
                  Check Sentence
                </Button>
              </Group>
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
                  Next Sentence
                </Button>
              </>
            )}
          </Stack>
        </Card>
      )}
    </Stack>
  );
};

export default SentenceConstructionPage;
