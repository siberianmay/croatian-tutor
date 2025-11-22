import React from 'react';
import { Title, Text, Stack, Card, Badge, Group } from '@mantine/core';

const ProgressPage: React.FC = () => {
  return (
    <Stack gap="lg">
      <div>
        <Title order={1}>Your Progress</Title>
        <Text c="dimmed" mt="sm">
          Track your Croatian learning journey
        </Text>
      </div>

      <Card shadow="sm" padding="lg" radius="md" withBorder>
        <Group justify="space-between" mb="md">
          <Title order={3}>Statistics</Title>
          <Badge color="violet">Coming Soon</Badge>
        </Group>
        <Text c="dimmed">
          Your learning statistics, streaks, and progress charts will appear here once you start
          practicing.
        </Text>
      </Card>
    </Stack>
  );
};

export default ProgressPage;
