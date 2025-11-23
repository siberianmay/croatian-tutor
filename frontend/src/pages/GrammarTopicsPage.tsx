import React, { useState, useMemo } from 'react';
import {
  Title,
  Text,
  Stack,
  Table,
  Button,
  Group,
  Badge,
  Modal,
  Alert,
  Paper,
  SegmentedControl,
  Loader,
} from '@mantine/core';
import { TableSkeleton } from '~components/skeletons';
import { useDisclosure } from '@mantine/hooks';
import { IconCheck, IconEye, IconBook } from '@tabler/icons-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { topicApi } from '~services/topicApi';
import type { GrammarTopic, CEFRLevel } from '~types';

const CEFR_LEVELS: CEFRLevel[] = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'];

const CEFR_COLORS: Record<CEFRLevel, string> = {
  A1: 'green',
  A2: 'lime',
  B1: 'yellow',
  B2: 'orange',
  C1: 'red',
  C2: 'grape',
};

const GrammarTopicsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [opened, { open, close }] = useDisclosure(false);
  const [selectedTopic, setSelectedTopic] = useState<GrammarTopic | null>(null);
  const [levelFilter, setLevelFilter] = useState<string>('all');

  const { data: topics, isLoading, error } = useQuery({
    queryKey: ['topics'],
    queryFn: () => topicApi.list({ limit: 500 }),
  });

  const markLearntMutation = useMutation({
    mutationFn: (topicId: number) => topicApi.markLearnt(topicId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['topics'] });
    },
  });

  const generateDescriptionMutation = useMutation({
    mutationFn: (topicId: number) => topicApi.generateDescription(topicId),
    onSuccess: (updatedTopic) => {
      queryClient.invalidateQueries({ queryKey: ['topics'] });
      setSelectedTopic(updatedTopic);
    },
  });

  const filteredTopics = useMemo(() => {
    if (!topics) return [];
    if (levelFilter === 'all') return topics;
    return topics.filter((t) => t.cefr_level === levelFilter);
  }, [topics, levelFilter]);

  const topicsByLevel = useMemo(() => {
    const grouped: Record<CEFRLevel, GrammarTopic[]> = {
      A1: [], A2: [], B1: [], B2: [], C1: [], C2: [],
    };
    filteredTopics.forEach((topic) => {
      grouped[topic.cefr_level].push(topic);
    });
    return grouped;
  }, [filteredTopics]);

  const stats = useMemo(() => {
    if (!topics) return { total: 0, learnt: 0 };
    return {
      total: topics.length,
      learnt: topics.filter((t) => t.is_learnt).length,
    };
  }, [topics]);

  const handleViewDescription = (topic: GrammarTopic) => {
    setSelectedTopic(topic);
    open();
  };

  const handleMarkLearnt = (topicId: number) => {
    markLearntMutation.mutate(topicId);
  };

  const handleGenerateDescription = () => {
    if (selectedTopic) {
      generateDescriptionMutation.mutate(selectedTopic.id);
    }
  };

  if (error) {
    return (
      <Alert color="red" title="Error loading topics">
        {(error as Error).message}
      </Alert>
    );
  }

  return (
    <Stack gap="lg">
      <div>
        <Title order={1}>Grammar Topics</Title>
        <Text c="dimmed" mt="sm">
          Review and mark grammar topics as learned. Exercises will only use grammar you've learned.
        </Text>
      </div>

      <Paper p="md" withBorder>
        <Group justify="space-between" mb="md">
          <Group gap="md">
            <Badge size="lg" variant="light">
              {stats.learnt} / {stats.total} learned
            </Badge>
          </Group>
          <SegmentedControl
            value={levelFilter}
            onChange={setLevelFilter}
            data={[
              { value: 'all', label: 'All' },
              ...CEFR_LEVELS.map((level) => ({ value: level, label: level })),
            ]}
          />
        </Group>

        {isLoading ? (
          <TableSkeleton columns={4} rows={10} />
        ) : filteredTopics.length > 0 ? (
          <Stack gap="xl">
            {CEFR_LEVELS.map((level) => {
              const levelTopics = topicsByLevel[level];
              if (levelTopics.length === 0) return null;

              return (
                <div key={level}>
                  <Group gap="sm" mb="sm">
                    <Badge color={CEFR_COLORS[level]} size="lg">
                      {level}
                    </Badge>
                    <Text size="sm" c="dimmed">
                      {levelTopics.filter((t) => t.is_learnt).length} / {levelTopics.length} learned
                    </Text>
                  </Group>
                  <Table.ScrollContainer minWidth={600}>
                    <Table striped highlightOnHover>
                      <Table.Thead>
                        <Table.Tr>
                          <Table.Th>Topic</Table.Th>
                          <Table.Th>Status</Table.Th>
                          <Table.Th>Actions</Table.Th>
                        </Table.Tr>
                      </Table.Thead>
                      <Table.Tbody>
                        {levelTopics.map((topic) => (
                          <Table.Tr key={topic.id}>
                            <Table.Td fw={500}>{topic.name}</Table.Td>
                            <Table.Td>
                              {topic.is_learnt ? (
                                <Badge color="green" leftSection={<IconCheck size={12} />}>
                                  Learned
                                </Badge>
                              ) : (
                                <Badge color="gray" variant="light">
                                  Not learned
                                </Badge>
                              )}
                            </Table.Td>
                            <Table.Td>
                              <Group gap="xs">
                                <Button
                                  variant="light"
                                  size="xs"
                                  leftSection={<IconEye size={14} />}
                                  onClick={() => handleViewDescription(topic)}
                                >
                                  View
                                </Button>
                                {!topic.is_learnt && (
                                  <Button
                                    variant="filled"
                                    size="xs"
                                    color="green"
                                    leftSection={<IconCheck size={14} />}
                                    onClick={() => handleMarkLearnt(topic.id)}
                                    loading={markLearntMutation.isPending && markLearntMutation.variables === topic.id}
                                  >
                                    Mark Learned
                                  </Button>
                                )}
                              </Group>
                            </Table.Td>
                          </Table.Tr>
                        ))}
                      </Table.Tbody>
                    </Table>
                  </Table.ScrollContainer>
                </div>
              );
            })}
          </Stack>
        ) : (
          <Text c="dimmed" ta="center" py="xl">
            No grammar topics found.
          </Text>
        )}
      </Paper>

      <Modal
        opened={opened}
        onClose={close}
        title={selectedTopic?.name || 'Topic Description'}
        size="lg"
      >
        {selectedTopic && (
          <Stack gap="md">
            <Group gap="sm">
              <Badge color={CEFR_COLORS[selectedTopic.cefr_level]}>
                {selectedTopic.cefr_level}
              </Badge>
              {selectedTopic.is_learnt && (
                <Badge color="green" leftSection={<IconCheck size={12} />}>
                  Learned
                </Badge>
              )}
            </Group>

            {selectedTopic.rule_description ? (
              <Paper p="md" withBorder style={{ maxHeight: '60vh', overflow: 'auto' }}>
                <Markdown remarkPlugins={[remarkGfm]}>{selectedTopic.rule_description}</Markdown>
              </Paper>
            ) : (
              <Alert color="yellow" title="No description available">
                <Stack gap="sm">
                  <Text size="sm">
                    This topic doesn't have a description yet. Generate one using AI?
                  </Text>
                  <Button
                    leftSection={generateDescriptionMutation.isPending ? <Loader size={14} /> : <IconBook size={14} />}
                    onClick={handleGenerateDescription}
                    loading={generateDescriptionMutation.isPending}
                    variant="light"
                  >
                    Generate Description
                  </Button>
                </Stack>
              </Alert>
            )}

            <Group justify="flex-end" mt="md">
              {!selectedTopic.is_learnt && (
                <Button
                  color="green"
                  leftSection={<IconCheck size={16} />}
                  onClick={() => {
                    handleMarkLearnt(selectedTopic.id);
                    close();
                  }}
                  loading={markLearntMutation.isPending}
                >
                  Mark as Learned
                </Button>
              )}
              <Button variant="subtle" onClick={close}>
                Close
              </Button>
            </Group>
          </Stack>
        )}
      </Modal>
    </Stack>
  );
};

export default GrammarTopicsPage;
