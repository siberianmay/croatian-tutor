import React, { useState, useEffect, useCallback } from 'react';
import {
  Modal,
  Tabs,
  Stack,
  Text,
  Group,
  Badge,
  Card,
  Table,
  Progress,
  ThemeIcon,
  Alert,
  Skeleton,
  SimpleGrid,
  Tooltip,
} from '@mantine/core';
import {
  IconBug,
  IconCalendar,
  IconTrendingUp,
  IconChartBar,
  IconAlertTriangle,
  IconCheck,
  IconArrowUp,
  IconArrowDown,
  IconMinus,
} from '@tabler/icons-react';
import { analyticsApi } from '~services/analyticsApi';
import { useLanguage } from '~contexts/LanguageContext';
import type {
  LeechesResponse,
  ForecastResponse,
  VelocityResponse,
  DifficultyResponse,
} from '~types';

interface AnalyticsModalProps {
  opened: boolean;
  onClose: () => void;
}

const AnalyticsModal: React.FC<AnalyticsModalProps> = ({ opened, onClose }) => {
  const { language } = useLanguage();
  const languageName = language?.name ?? 'Word';

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [leeches, setLeeches] = useState<LeechesResponse | null>(null);
  const [forecast, setForecast] = useState<ForecastResponse | null>(null);
  const [velocity, setVelocity] = useState<VelocityResponse | null>(null);
  const [difficulty, setDifficulty] = useState<DifficultyResponse | null>(null);

  const fetchData = useCallback(async () => {
    if (!opened) return;

    setLoading(true);
    setError(null);
    try {
      const [leechData, forecastData, velocityData, difficultyData] = await Promise.all([
        analyticsApi.getLeeches(10),
        analyticsApi.getForecast(7),
        analyticsApi.getVelocity(),
        analyticsApi.getDifficulty(),
      ]);
      setLeeches(leechData);
      setForecast(forecastData);
      setVelocity(velocityData);
      setDifficulty(difficultyData);
    } catch (err) {
      console.error('Failed to fetch analytics:', err);
      setError('Failed to load analytics data.');
    } finally {
      setLoading(false);
    }
  }, [opened]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving':
        return <IconArrowUp size={16} color="green" />;
      case 'declining':
        return <IconArrowDown size={16} color="red" />;
      default:
        return <IconMinus size={16} color="gray" />;
    }
  };

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'improving':
        return 'green';
      case 'declining':
        return 'red';
      default:
        return 'gray';
    }
  };

  return (
    <Modal
      opened={opened}
      onClose={onClose}
      title="Advanced Analytics"
      size="xl"
      centered
    >
      {error && (
        <Alert color="red" icon={<IconAlertTriangle size={16} />} mb="md">
          {error}
        </Alert>
      )}

      {loading ? (
        <Stack gap="md">
          <Skeleton height={40} />
          <Skeleton height={200} />
        </Stack>
      ) : (
        <Tabs defaultValue="velocity">
          <Tabs.List mb="md">
            <Tabs.Tab value="velocity" leftSection={<IconTrendingUp size={16} />}>
              Velocity
            </Tabs.Tab>
            <Tabs.Tab value="forecast" leftSection={<IconCalendar size={16} />}>
              Forecast
            </Tabs.Tab>
            <Tabs.Tab value="difficulty" leftSection={<IconChartBar size={16} />}>
              Difficulty
            </Tabs.Tab>
            <Tabs.Tab
              value="leeches"
              leftSection={<IconBug size={16} />}
              rightSection={
                leeches && leeches.total_leeches > 0 ? (
                  <Badge size="xs" color="red">
                    {leeches.total_leeches}
                  </Badge>
                ) : null
              }
            >
              Leeches
            </Tabs.Tab>
          </Tabs.List>

          {/* Velocity Tab */}
          <Tabs.Panel value="velocity">
            {velocity && (
              <Stack gap="md">
                <Group justify="space-between">
                  <Text fw={500}>Learning Trend</Text>
                  <Badge
                    color={getTrendColor(velocity.velocity_trend)}
                    leftSection={getTrendIcon(velocity.velocity_trend)}
                  >
                    {velocity.velocity_trend}
                  </Badge>
                </Group>

                <SimpleGrid cols={2} spacing="md">
                  <Card withBorder padding="sm">
                    <Text size="xs" c="dimmed">
                      Words Added This Week
                    </Text>
                    <Text size="xl" fw={700}>
                      {velocity.words_added_this_week}
                    </Text>
                    <Text size="xs" c="dimmed">
                      vs {velocity.words_added_last_week} last week
                    </Text>
                  </Card>

                  <Card withBorder padding="sm">
                    <Text size="xs" c="dimmed">
                      Words Mastered This Week
                    </Text>
                    <Text size="xl" fw={700}>
                      {velocity.words_mastered_this_week}
                    </Text>
                    <Text size="xs" c="dimmed">
                      {velocity.words_mastered_total} total mastered
                    </Text>
                  </Card>

                  <Card withBorder padding="sm">
                    <Text size="xs" c="dimmed">
                      Retention Rate
                    </Text>
                    <Group gap="xs" align="baseline">
                      <Text size="xl" fw={700}>
                        {Math.round(velocity.retention_rate * 100)}%
                      </Text>
                      <ThemeIcon
                        size="sm"
                        color={velocity.retention_rate >= 0.7 ? 'green' : 'orange'}
                        variant="light"
                      >
                        {velocity.retention_rate >= 0.7 ? (
                          <IconCheck size={12} />
                        ) : (
                          <IconAlertTriangle size={12} />
                        )}
                      </ThemeIcon>
                    </Group>
                    <Progress
                      value={velocity.retention_rate * 100}
                      color={velocity.retention_rate >= 0.7 ? 'green' : 'orange'}
                      size="sm"
                      mt="xs"
                    />
                  </Card>

                  <Card withBorder padding="sm">
                    <Text size="xs" c="dimmed">
                      Avg Ease Factor
                    </Text>
                    <Text size="xl" fw={700}>
                      {velocity.avg_ease_factor.toFixed(2)}
                    </Text>
                    <Text size="xs" c="dimmed">
                      SM-2 difficulty (2.5 = normal)
                    </Text>
                  </Card>
                </SimpleGrid>
              </Stack>
            )}
          </Tabs.Panel>

          {/* Forecast Tab */}
          <Tabs.Panel value="forecast">
            {forecast && (
              <Stack gap="md">
                <Group justify="space-between">
                  <div>
                    <Text fw={500}>Review Forecast</Text>
                    <Text size="xs" c="dimmed">
                      Upcoming reviews for the next 7 days
                    </Text>
                  </div>
                  {forecast.overdue > 0 && (
                    <Badge color="red" size="lg">
                      {forecast.overdue} overdue
                    </Badge>
                  )}
                </Group>

                <SimpleGrid cols={7} spacing="xs">
                  {forecast.forecast.map((day) => (
                    <Tooltip
                      key={day.date}
                      label={`${day.date}: ${day.count} reviews`}
                    >
                      <Card
                        withBorder
                        padding="xs"
                        style={{
                          backgroundColor: day.is_today
                            ? 'var(--mantine-color-blue-light)'
                            : undefined,
                        }}
                      >
                        <Text size="xs" c="dimmed" ta="center">
                          {new Date(day.date).toLocaleDateString('en-US', {
                            weekday: 'short',
                          })}
                        </Text>
                        <Text
                          size="lg"
                          fw={700}
                          ta="center"
                          c={day.count > 0 ? 'blue' : 'dimmed'}
                        >
                          {day.count}
                        </Text>
                        {day.is_today && (
                          <Badge size="xs" color="blue" fullWidth>
                            Today
                          </Badge>
                        )}
                      </Card>
                    </Tooltip>
                  ))}
                </SimpleGrid>

                <Card withBorder padding="sm">
                  <Group justify="space-between">
                    <Text size="sm">Total upcoming (7 days)</Text>
                    <Text fw={500}>{forecast.total_upcoming}</Text>
                  </Group>
                </Card>
              </Stack>
            )}
          </Tabs.Panel>

          {/* Difficulty Tab */}
          <Tabs.Panel value="difficulty">
            {difficulty && (
              <Stack gap="md">
                {(difficulty.hardest_pos || difficulty.hardest_level) && (
                  <Alert color="orange" icon={<IconAlertTriangle size={16} />}>
                    <Group gap="xs">
                      <Text size="sm">Hardest areas:</Text>
                      {difficulty.hardest_pos && (
                        <Badge color="orange">{difficulty.hardest_pos}</Badge>
                      )}
                      {difficulty.hardest_level && (
                        <Badge color="orange">{difficulty.hardest_level}</Badge>
                      )}
                    </Group>
                  </Alert>
                )}

                <Text fw={500}>By Part of Speech</Text>
                <Table highlightOnHover>
                  <Table.Thead>
                    <Table.Tr>
                      <Table.Th>Type</Table.Th>
                      <Table.Th>Count</Table.Th>
                      <Table.Th>Avg Mastery</Table.Th>
                      <Table.Th>Failure Rate</Table.Th>
                    </Table.Tr>
                  </Table.Thead>
                  <Table.Tbody>
                    {Object.entries(difficulty.by_pos)
                      .sort((a, b) => b[1].failure_rate - a[1].failure_rate)
                      .map(([pos, stats]) => (
                        <Table.Tr key={pos}>
                          <Table.Td>
                            <Badge
                              variant={pos === difficulty.hardest_pos ? 'filled' : 'light'}
                              color={pos === difficulty.hardest_pos ? 'orange' : 'gray'}
                            >
                              {pos}
                            </Badge>
                          </Table.Td>
                          <Table.Td>{stats.count}</Table.Td>
                          <Table.Td>{stats.avg_mastery}/10</Table.Td>
                          <Table.Td>
                            <Text c={stats.failure_rate > 0.3 ? 'red' : 'green'}>
                              {Math.round(stats.failure_rate * 100)}%
                            </Text>
                          </Table.Td>
                        </Table.Tr>
                      ))}
                  </Table.Tbody>
                </Table>

                <Text fw={500}>By CEFR Level</Text>
                <Table highlightOnHover>
                  <Table.Thead>
                    <Table.Tr>
                      <Table.Th>Level</Table.Th>
                      <Table.Th>Count</Table.Th>
                      <Table.Th>Avg Mastery</Table.Th>
                      <Table.Th>Failure Rate</Table.Th>
                    </Table.Tr>
                  </Table.Thead>
                  <Table.Tbody>
                    {Object.entries(difficulty.by_level)
                      .sort((a, b) => b[1].failure_rate - a[1].failure_rate)
                      .map(([level, stats]) => (
                        <Table.Tr key={level}>
                          <Table.Td>
                            <Badge
                              variant={level === difficulty.hardest_level ? 'filled' : 'light'}
                              color={level === difficulty.hardest_level ? 'orange' : 'blue'}
                            >
                              {level}
                            </Badge>
                          </Table.Td>
                          <Table.Td>{stats.count}</Table.Td>
                          <Table.Td>{stats.avg_mastery}/10</Table.Td>
                          <Table.Td>
                            <Text c={stats.failure_rate > 0.3 ? 'red' : 'green'}>
                              {Math.round(stats.failure_rate * 100)}%
                            </Text>
                          </Table.Td>
                        </Table.Tr>
                      ))}
                  </Table.Tbody>
                </Table>
              </Stack>
            )}
          </Tabs.Panel>

          {/* Leeches Tab */}
          <Tabs.Panel value="leeches">
            {leeches && (
              <Stack gap="md">
                <Alert
                  color={leeches.total_leeches > 0 ? 'orange' : 'green'}
                  icon={
                    leeches.total_leeches > 0 ? (
                      <IconBug size={16} />
                    ) : (
                      <IconCheck size={16} />
                    )
                  }
                >
                  {leeches.total_leeches > 0 ? (
                    <>
                      <Text size="sm" fw={500}>
                        {leeches.total_leeches} leech word(s) detected
                      </Text>
                      <Text size="xs">
                        Words with ≥{Math.round(leeches.threshold.failure_rate * 100)}% failure rate
                        after {leeches.threshold.min_attempts}+ attempts. Consider using mnemonics
                        or breaking them down.
                      </Text>
                    </>
                  ) : (
                    <Text size="sm">No leeches detected. Keep up the good work!</Text>
                  )}
                </Alert>

                {leeches.leeches.length > 0 && (
                  <Table highlightOnHover>
                    <Table.Thead>
                      <Table.Tr>
                        <Table.Th>{languageName}</Table.Th>
                        <Table.Th>English</Table.Th>
                        <Table.Th>Stats</Table.Th>
                        <Table.Th>Failure Rate</Table.Th>
                      </Table.Tr>
                    </Table.Thead>
                    <Table.Tbody>
                      {leeches.leeches.map((word) => (
                        <Table.Tr key={word.id}>
                          <Table.Td>
                            <Text fw={500}>{word.croatian}</Text>
                          </Table.Td>
                          <Table.Td>{word.english}</Table.Td>
                          <Table.Td>
                            <Group gap="xs">
                              <Text size="xs" c="green">
                                ✓{word.correct_count}
                              </Text>
                              <Text size="xs" c="red">
                                ✗{word.wrong_count}
                              </Text>
                            </Group>
                          </Table.Td>
                          <Table.Td>
                            <Badge color="red">
                              {Math.round(word.failure_rate * 100)}%
                            </Badge>
                          </Table.Td>
                        </Table.Tr>
                      ))}
                    </Table.Tbody>
                  </Table>
                )}
              </Stack>
            )}
          </Tabs.Panel>
        </Tabs>
      )}
    </Modal>
  );
};

export default AnalyticsModal;
