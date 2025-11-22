import React, { useState } from 'react';
import {
  Title,
  Text,
  Stack,
  Card,
  Button,
  Group,
  Badge,
  TextInput,
  SegmentedControl,
  Center,
  Loader,
  Alert,
  Paper,
  Progress,
  Box,
} from '@mantine/core';
import { IconCheck, IconX, IconArrowRight, IconRefresh } from '@tabler/icons-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { drillApi } from '~services/drillApi';
import { wordApi } from '~services/wordApi';
import type { DrillItem, DrillSessionResponse } from '~types';

type DrillMode = 'vocabulary_cr_en' | 'vocabulary_en_cr';

const PracticePage: React.FC = () => {
  const queryClient = useQueryClient();
  const [mode, setMode] = useState<DrillMode>('vocabulary_cr_en');
  const [session, setSession] = useState<DrillSessionResponse | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [userAnswer, setUserAnswer] = useState('');
  const [showResult, setShowResult] = useState(false);
  const [lastResult, setLastResult] = useState<{ correct: boolean; expected: string } | null>(null);
  const [score, setScore] = useState({ correct: 0, wrong: 0 });

  const { data: dueCount, isLoading: loadingDue } = useQuery({
    queryKey: ['words', 'due', 'count'],
    queryFn: () => wordApi.countDue(),
  });

  const startMutation = useMutation({
    mutationFn: () => drillApi.startSession({ exercise_type: mode, count: 10 }),
    onSuccess: (data) => {
      setSession(data);
      setCurrentIndex(0);
      setScore({ correct: 0, wrong: 0 });
      setShowResult(false);
      setLastResult(null);
      setUserAnswer('');
    },
  });

  const checkMutation = useMutation({
    mutationFn: (item: DrillItem) =>
      drillApi.checkAnswer({
        word_id: item.word_id,
        user_answer: userAnswer,
        exercise_type: mode,
      }),
    onSuccess: (result) => {
      setLastResult({ correct: result.correct, expected: result.expected_answer });
      setShowResult(true);
      setScore((prev) => ({
        correct: prev.correct + (result.correct ? 1 : 0),
        wrong: prev.wrong + (result.correct ? 0 : 1),
      }));
    },
  });

  const reviewMutation = useMutation({
    mutationFn: ({ wordId, correct }: { wordId: number; correct: boolean }) =>
      wordApi.review(wordId, { correct }),
  });

  const currentItem = session?.items[currentIndex];

  const handleSubmit = () => {
    if (!currentItem || !userAnswer.trim()) return;
    checkMutation.mutate(currentItem);
  };

  const handleNext = () => {
    if (!currentItem || lastResult === null) return;

    // Submit review to update SRS
    reviewMutation.mutate({ wordId: currentItem.word_id, correct: lastResult.correct });

    // Move to next or finish
    if (currentIndex < (session?.items.length ?? 0) - 1) {
      setCurrentIndex((prev) => prev + 1);
      setUserAnswer('');
      setShowResult(false);
      setLastResult(null);
    } else {
      // Session complete
      setSession(null);
      queryClient.invalidateQueries({ queryKey: ['words'] });
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      if (showResult) {
        handleNext();
      } else {
        handleSubmit();
      }
    }
  };

  // Session not started
  if (!session) {
    const isComplete = session === null && score.correct + score.wrong > 0;

    return (
      <Stack gap="lg">
        <div>
          <Title order={1}>Practice</Title>
          <Text c="dimmed" mt="sm">
            Test your vocabulary with flashcard drills
          </Text>
        </div>

        {isComplete && (
          <Alert color="green" title="Session Complete!">
            You scored {score.correct} out of {score.correct + score.wrong} (
            {Math.round((score.correct / (score.correct + score.wrong)) * 100)}%)
          </Alert>
        )}

        <Paper p="xl" withBorder>
          <Stack gap="lg" align="center">
            {loadingDue ? (
              <Loader />
            ) : (
              <>
                {dueCount !== undefined && (
                  <Badge size="xl" color={dueCount > 0 ? 'orange' : 'green'}>
                    {dueCount > 0 ? `${dueCount} words due for review` : 'No words due'}
                  </Badge>
                )}

                <Text size="lg" ta="center">
                  Choose your practice mode:
                </Text>

                <SegmentedControl
                  value={mode}
                  onChange={(v) => setMode(v as DrillMode)}
                  data={[
                    { label: 'Croatian → English', value: 'vocabulary_cr_en' },
                    { label: 'English → Croatian', value: 'vocabulary_en_cr' },
                  ]}
                  size="md"
                />

                <Button
                  size="lg"
                  onClick={() => startMutation.mutate()}
                  loading={startMutation.isPending}
                  leftSection={<IconRefresh size={20} />}
                >
                  {isComplete ? 'Practice Again' : 'Start Practice'}
                </Button>
              </>
            )}
          </Stack>
        </Paper>
      </Stack>
    );
  }

  // Active session
  const progressPercent = ((currentIndex + 1) / session.items.length) * 100;

  return (
    <Stack gap="lg">
      <Group justify="space-between">
        <div>
          <Title order={1}>Practice</Title>
          <Text c="dimmed">
            {mode === 'vocabulary_cr_en' ? 'Croatian → English' : 'English → Croatian'}
          </Text>
        </div>
        <Badge size="lg">
          {currentIndex + 1} / {session.items.length}
        </Badge>
      </Group>

      <Progress value={progressPercent} size="lg" radius="xl" />

      <Group justify="center" gap="md">
        <Badge color="green" size="lg">
          Correct: {score.correct}
        </Badge>
        <Badge color="red" size="lg">
          Wrong: {score.wrong}
        </Badge>
      </Group>

      {currentItem && (
        <Card shadow="md" padding="xl" radius="lg" withBorder>
          <Stack gap="xl" align="center">
            <Box ta="center">
              <Text size="sm" c="dimmed" mb="xs">
                {currentItem.part_of_speech}
                {currentItem.gender && ` (${currentItem.gender})`}
              </Text>
              <Title order={2} size="2.5rem">
                {currentItem.prompt}
              </Title>
            </Box>

            {!showResult ? (
              <TextInput
                placeholder="Type your answer..."
                value={userAnswer}
                onChange={(e) => setUserAnswer(e.target.value)}
                onKeyPress={handleKeyPress}
                size="lg"
                style={{ width: '100%', maxWidth: 400 }}
                autoFocus
              />
            ) : (
              <Center>
                {lastResult?.correct ? (
                  <Alert
                    icon={<IconCheck size={24} />}
                    color="green"
                    title="Correct!"
                    style={{ minWidth: 300 }}
                  >
                    {currentItem.expected_answer}
                  </Alert>
                ) : (
                  <Alert
                    icon={<IconX size={24} />}
                    color="red"
                    title="Incorrect"
                    style={{ minWidth: 300 }}
                  >
                    <Text>Your answer: {userAnswer}</Text>
                    <Text fw={600}>Correct: {lastResult?.expected}</Text>
                  </Alert>
                )}
              </Center>
            )}

            {!showResult ? (
              <Button
                size="lg"
                onClick={handleSubmit}
                loading={checkMutation.isPending}
                disabled={!userAnswer.trim()}
              >
                Check Answer
              </Button>
            ) : (
              <Button
                size="lg"
                onClick={handleNext}
                rightSection={<IconArrowRight size={20} />}
              >
                {currentIndex < session.items.length - 1 ? 'Next Word' : 'Finish'}
              </Button>
            )}
          </Stack>
        </Card>
      )}
    </Stack>
  );
};

export default PracticePage;
