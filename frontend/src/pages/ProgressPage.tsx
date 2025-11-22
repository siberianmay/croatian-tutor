import React, { useState, useEffect, useCallback } from 'react';
import {
  Title,
  Text,
  Stack,
  Card,
  Badge,
  Group,
  SimpleGrid,
  RingProgress,
  Progress,
  ThemeIcon,
  Button,
  Alert,
  Loader,
  Center,
  Table,
  Divider,
} from '@mantine/core';
import {
  IconBook,
  IconFlame,
  IconTarget,
  IconAlertCircle,
  IconTrophy,
  IconRefresh,
  IconVocabulary,
  IconBooks,
  IconClock,
  IconChartBar,
} from '@tabler/icons-react';
import { useNavigate } from 'react-router-dom';
import { progressApi } from '~services/progressApi';
import type {
  ProgressSummary,
  VocabularyStats,
  TopicStats,
  ActivityStats,
  ErrorPatterns,
} from '~types';

// Stat card component
interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  color: string;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, subtitle, icon, color }) => (
  <Card shadow="sm" padding="lg" radius="md" withBorder>
    <Group justify="space-between" mb="xs">
      <Text size="sm" c="dimmed" fw={500}>
        {title}
      </Text>
      <ThemeIcon color={color} variant="light" size="lg">
        {icon}
      </ThemeIcon>
    </Group>
    <Text fw={700} size="xl">
      {value}
    </Text>
    {subtitle && (
      <Text size="xs" c="dimmed" mt={4}>
        {subtitle}
      </Text>
    )}
  </Card>
);

const ProgressPage: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [summary, setSummary] = useState<ProgressSummary | null>(null);
  const [vocabStats, setVocabStats] = useState<VocabularyStats | null>(null);
  const [topicStats, setTopicStats] = useState<TopicStats | null>(null);
  const [activityStats, setActivityStats] = useState<ActivityStats | null>(null);
  const [errorPatterns, setErrorPatterns] = useState<ErrorPatterns | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [summaryData, vocabData, topicData, activityData, errorData] = await Promise.all([
        progressApi.getSummary(),
        progressApi.getVocabularyStats(),
        progressApi.getTopicStats(),
        progressApi.getActivity(14),
        progressApi.getErrorPatterns(),
      ]);
      setSummary(summaryData);
      setVocabStats(vocabData);
      setTopicStats(topicData);
      setActivityStats(activityData);
      setErrorPatterns(errorData);
    } catch (err) {
      console.error('Failed to fetch progress data:', err);
      setError('Failed to load progress data. Please try again.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  if (loading) {
    return (
      <Center h={400}>
        <Loader size="lg" />
      </Center>
    );
  }

  if (error) {
    return (
      <Alert icon={<IconAlertCircle size={16} />} title="Error" color="red">
        {error}
        <Button variant="light" size="xs" mt="sm" onClick={fetchData}>
          Retry
        </Button>
      </Alert>
    );
  }

  if (!summary) {
    return (
      <Alert icon={<IconAlertCircle size={16} />} title="No Data">
        No progress data available yet. Start practicing to see your stats!
      </Alert>
    );
  }

  const masteryPercent =
    summary.total_words > 0
      ? Math.round((summary.mastered_words / summary.total_words) * 100)
      : 0;

  return (
    <Stack gap="xl">
      {/* Header */}
      <Group justify="space-between">
        <div>
          <Title order={1}>Your Progress</Title>
          <Text c="dimmed" mt="sm">
            Track your Croatian learning journey
          </Text>
        </div>
        <Button
          variant="light"
          leftSection={<IconRefresh size={16} />}
          onClick={fetchData}
        >
          Refresh
        </Button>
      </Group>

      {/* Summary Stats */}
      <SimpleGrid cols={{ base: 2, sm: 3, lg: 6 }} spacing="md">
        <StatCard
          title="Level"
          value={summary.current_level}
          subtitle="CEFR Level"
          icon={<IconTrophy size={20} />}
          color="violet"
        />
        <StatCard
          title="Streak"
          value={`${summary.streak_days} days`}
          subtitle="Keep it up!"
          icon={<IconFlame size={20} />}
          color="orange"
        />
        <StatCard
          title="Total Words"
          value={summary.total_words}
          subtitle={`${summary.mastered_words} mastered`}
          icon={<IconVocabulary size={20} />}
          color="blue"
        />
        <StatCard
          title="Due Today"
          value={summary.words_due_today}
          subtitle="Words to review"
          icon={<IconTarget size={20} />}
          color="green"
        />
        <StatCard
          title="Exercises"
          value={summary.total_exercises}
          subtitle="Completed"
          icon={<IconBooks size={20} />}
          color="teal"
        />
        <StatCard
          title="Errors"
          value={summary.total_errors}
          subtitle="To learn from"
          icon={<IconAlertCircle size={20} />}
          color="red"
        />
      </SimpleGrid>

      {/* Main Content Grid */}
      <SimpleGrid cols={{ base: 1, md: 2 }} spacing="lg">
        {/* Vocabulary Breakdown */}
        <Card shadow="sm" padding="lg" radius="md" withBorder>
          <Group justify="space-between" mb="md">
            <Title order={4}>Vocabulary Mastery</Title>
            <Badge color="blue">{summary.total_words} words</Badge>
          </Group>

          <Group justify="center" mb="md">
            <RingProgress
              size={140}
              thickness={14}
              roundCaps
              sections={[
                {
                  value: vocabStats?.by_mastery.mastered
                    ? (vocabStats.by_mastery.mastered / Math.max(summary.total_words, 1)) * 100
                    : 0,
                  color: 'green',
                },
                {
                  value: vocabStats?.by_mastery.learning
                    ? (vocabStats.by_mastery.learning / Math.max(summary.total_words, 1)) * 100
                    : 0,
                  color: 'yellow',
                },
                {
                  value: vocabStats?.by_mastery.new
                    ? (vocabStats.by_mastery.new / Math.max(summary.total_words, 1)) * 100
                    : 0,
                  color: 'gray',
                },
              ]}
              label={
                <Text ta="center" fw={700} size="lg">
                  {masteryPercent}%
                </Text>
              }
            />
          </Group>

          <Stack gap="xs">
            <Group justify="space-between">
              <Group gap="xs">
                <Badge color="green" size="sm" variant="dot" />
                <Text size="sm">Mastered</Text>
              </Group>
              <Text size="sm" fw={500}>
                {vocabStats?.by_mastery.mastered ?? 0}
              </Text>
            </Group>
            <Group justify="space-between">
              <Group gap="xs">
                <Badge color="yellow" size="sm" variant="dot" />
                <Text size="sm">Learning</Text>
              </Group>
              <Text size="sm" fw={500}>
                {vocabStats?.by_mastery.learning ?? 0}
              </Text>
            </Group>
            <Group justify="space-between">
              <Group gap="xs">
                <Badge color="gray" size="sm" variant="dot" />
                <Text size="sm">New</Text>
              </Group>
              <Text size="sm" fw={500}>
                {vocabStats?.by_mastery.new ?? 0}
              </Text>
            </Group>
          </Stack>

          <Divider my="md" />

          <Text size="sm" fw={500} mb="xs">
            Words by Level
          </Text>
          <Stack gap="xs">
            {vocabStats?.by_level &&
              Object.entries(vocabStats.by_level).map(([level, count]) => (
                <Group key={level} justify="space-between">
                  <Badge variant="outline" size="sm">
                    {level}
                  </Badge>
                  <Text size="sm">{count}</Text>
                </Group>
              ))}
            {(!vocabStats?.by_level || Object.keys(vocabStats.by_level).length === 0) && (
              <Text size="sm" c="dimmed">
                No words yet
              </Text>
            )}
          </Stack>

          <Button
            variant="light"
            fullWidth
            mt="md"
            onClick={() => navigate('/vocabulary')}
          >
            Manage Vocabulary
          </Button>
        </Card>

        {/* Topic Progress */}
        <Card shadow="sm" padding="lg" radius="md" withBorder>
          <Group justify="space-between" mb="md">
            <Title order={4}>Grammar Topics</Title>
            <Badge color="green">
              {topicStats?.practiced_topics ?? 0}/{topicStats?.total_topics ?? 0} practiced
            </Badge>
          </Group>

          {topicStats?.topics && topicStats.topics.length > 0 ? (
            <Stack gap="sm">
              {topicStats.topics.slice(0, 6).map((topic) => (
                <div key={topic.id}>
                  <Group justify="space-between" mb={4}>
                    <Text size="sm">{topic.name}</Text>
                    <Group gap="xs">
                      <Badge size="xs" variant="outline">
                        {topic.level}
                      </Badge>
                      <Text size="xs" c="dimmed">
                        {topic.attempts} attempts
                      </Text>
                    </Group>
                  </Group>
                  <Progress value={topic.mastery * 10} size="sm" color="blue" />
                </div>
              ))}
              {topicStats.topics.length > 6 && (
                <Text size="xs" c="dimmed" ta="center">
                  +{topicStats.topics.length - 6} more topics
                </Text>
              )}
            </Stack>
          ) : (
            <Text c="dimmed" size="sm">
              No grammar topics available. Add topics to track progress.
            </Text>
          )}

          <Button
            variant="light"
            fullWidth
            mt="md"
            onClick={() => navigate('/learn/grammar')}
          >
            Practice Grammar
          </Button>
        </Card>

        {/* Activity */}
        <Card shadow="sm" padding="lg" radius="md" withBorder>
          <Group justify="space-between" mb="md">
            <Title order={4}>Recent Activity</Title>
            <Badge color="teal">Last 14 days</Badge>
          </Group>

          {activityStats?.daily_activity && activityStats.daily_activity.length > 0 ? (
            <>
              <SimpleGrid cols={7} spacing={4} mb="md">
                {activityStats.daily_activity.slice(-14).map((day, idx) => (
                  <ThemeIcon
                    key={idx}
                    size="md"
                    variant={day.exercises > 0 ? 'filled' : 'light'}
                    color={day.exercises > 0 ? 'green' : 'gray'}
                    radius="sm"
                    title={`${day.date}: ${day.exercises} exercises`}
                  >
                    {day.exercises > 0 ? (
                      <IconClock size={12} />
                    ) : null}
                  </ThemeIcon>
                ))}
              </SimpleGrid>

              <Text size="sm" fw={500} mb="xs">
                Exercise Types
              </Text>
              <Stack gap="xs">
                {Object.entries(activityStats.exercise_breakdown)
                  .slice(0, 5)
                  .map(([type, count]) => (
                    <Group key={type} justify="space-between">
                      <Text size="sm">{type.replace(/_/g, ' ')}</Text>
                      <Badge size="sm">{count}</Badge>
                    </Group>
                  ))}
              </Stack>
            </>
          ) : (
            <Text c="dimmed" size="sm">
              No activity recorded yet. Start practicing!
            </Text>
          )}

          <Button
            variant="light"
            fullWidth
            mt="md"
            onClick={() => navigate('/learn')}
          >
            Start Exercises
          </Button>
        </Card>

        {/* Error Patterns / Weak Areas */}
        <Card shadow="sm" padding="lg" radius="md" withBorder>
          <Group justify="space-between" mb="md">
            <Title order={4}>Areas to Improve</Title>
            <Badge color="orange">
              {errorPatterns?.weak_areas.length ?? 0} weak areas
            </Badge>
          </Group>

          {errorPatterns?.weak_areas && errorPatterns.weak_areas.length > 0 ? (
            <Stack gap="md">
              {errorPatterns.weak_areas.map((area) => (
                <Card key={area.category} withBorder padding="sm" radius="sm">
                  <Group justify="space-between" mb="xs">
                    <Text size="sm" fw={500}>
                      {area.category.replace(/_/g, ' ')}
                    </Text>
                    <Badge color="red" size="sm">
                      {area.count} errors
                    </Badge>
                  </Group>
                  <Text size="xs" c="dimmed">
                    {area.suggestion}
                  </Text>
                </Card>
              ))}
            </Stack>
          ) : (
            <Text c="dimmed" size="sm">
              No error patterns detected yet. Keep practicing!
            </Text>
          )}

          {errorPatterns?.recent_errors && errorPatterns.recent_errors.length > 0 && (
            <>
              <Divider my="md" label="Recent Errors" labelPosition="center" />
              <Table highlightOnHover>
                <Table.Tbody>
                  {errorPatterns.recent_errors.slice(0, 3).map((err, idx) => (
                    <Table.Tr key={idx}>
                      <Table.Td>
                        <Text size="xs" c="dimmed">
                          {err.category.replace(/_/g, ' ')}
                        </Text>
                      </Table.Td>
                      <Table.Td>
                        <Text size="xs" td="line-through" c="red">
                          {err.details || '-'}
                        </Text>
                      </Table.Td>
                      <Table.Td>
                        <Text size="xs" c="green">
                          {err.correction || '-'}
                        </Text>
                      </Table.Td>
                    </Table.Tr>
                  ))}
                </Table.Tbody>
              </Table>
            </>
          )}

          <Button
            variant="light"
            fullWidth
            mt="md"
            onClick={() => navigate('/practice')}
          >
            Practice Drills
          </Button>
        </Card>
      </SimpleGrid>

      {/* Quick Actions */}
      <Card shadow="sm" padding="lg" radius="md" withBorder>
        <Title order={4} mb="md">
          Quick Actions
        </Title>
        <SimpleGrid cols={{ base: 2, sm: 4 }} spacing="md">
          <Button
            variant="light"
            color="blue"
            leftSection={<IconVocabulary size={18} />}
            onClick={() => navigate('/vocabulary')}
          >
            Add Words
          </Button>
          <Button
            variant="light"
            color="green"
            leftSection={<IconTarget size={18} />}
            onClick={() => navigate('/practice')}
          >
            Review Due ({summary.words_due_today})
          </Button>
          <Button
            variant="light"
            color="violet"
            leftSection={<IconBooks size={18} />}
            onClick={() => navigate('/learn/grammar')}
          >
            Grammar Drills
          </Button>
          <Button
            variant="light"
            color="orange"
            leftSection={<IconBook size={18} />}
            onClick={() => navigate('/learn/conversation')}
          >
            Chat with Tutor
          </Button>
        </SimpleGrid>
      </Card>
    </Stack>
  );
};

export default ProgressPage;
