import React from 'react';
import { Title, Text, Stack, Card, Badge, Group } from '@mantine/core';

const LearnPage: React.FC = () => {
  return (
    <Stack gap="lg">
      <div>
        <Title order={1}>Learn Croatian</Title>
        <Text c="dimmed" mt="sm">
          Browse vocabulary by topic and difficulty level
        </Text>
      </div>

      <Card shadow="sm" padding="lg" radius="md" withBorder>
        <Group justify="space-between" mb="md">
          <Title order={3}>Topics</Title>
          <Badge color="blue">Coming Soon</Badge>
        </Group>
        <Text c="dimmed">
          Vocabulary topics and lessons will appear here. Start a conversation with the AI tutor
          to begin learning!
        </Text>
      </Card>
    </Stack>
  );
};

export default LearnPage;
