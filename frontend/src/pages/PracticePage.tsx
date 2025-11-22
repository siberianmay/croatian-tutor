import React from 'react';
import { Title, Text, Stack, Card, Badge, Group } from '@mantine/core';

const PracticePage: React.FC = () => {
  return (
    <Stack gap="lg">
      <div>
        <Title order={1}>Practice</Title>
        <Text c="dimmed" mt="sm">
          Practice Croatian with AI-powered exercises and conversations
        </Text>
      </div>

      <Card shadow="sm" padding="lg" radius="md" withBorder>
        <Group justify="space-between" mb="md">
          <Title order={3}>AI Conversation</Title>
          <Badge color="green">Coming Soon</Badge>
        </Group>
        <Text c="dimmed">
          Practice Croatian conversation with our AI tutor. Get corrections, suggestions, and
          personalized feedback.
        </Text>
      </Card>
    </Stack>
  );
};

export default PracticePage;
