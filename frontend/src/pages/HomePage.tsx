import React from 'react';
import { Title, Text, Card, SimpleGrid, Button, Stack } from '@mantine/core';
import { IconBook, IconPencil, IconChartBar } from '@tabler/icons-react';
import { useNavigate } from 'react-router-dom';

const HomePage: React.FC = () => {
  const navigate = useNavigate();

  const features = [
    {
      title: 'Learn Vocabulary',
      description: 'Study Croatian words organized by topics and difficulty levels.',
      icon: IconBook,
      path: '/learn',
      color: 'blue',
    },
    {
      title: 'Practice Exercises',
      description: 'Test your knowledge with AI-powered exercises and conversations.',
      icon: IconPencil,
      path: '/practice',
      color: 'green',
    },
    {
      title: 'Track Progress',
      description: 'Monitor your learning progress and maintain your streak.',
      icon: IconChartBar,
      path: '/progress',
      color: 'violet',
    },
  ];

  return (
    <Stack gap="xl">
      <div>
        <Title order={1}>Welcome to Croatian Tutor</Title>
        <Text c="dimmed" size="lg" mt="sm">
          Your AI-powered companion for learning Croatian language
        </Text>
      </div>

      <SimpleGrid cols={{ base: 1, sm: 2, md: 3 }} spacing="lg">
        {features.map((feature) => (
          <Card key={feature.path} shadow="sm" padding="lg" radius="md" withBorder>
            <feature.icon size={32} color={`var(--mantine-color-${feature.color}-6)`} />
            <Title order={3} mt="md">
              {feature.title}
            </Title>
            <Text size="sm" c="dimmed" mt="sm">
              {feature.description}
            </Text>
            <Button
              variant="light"
              color={feature.color}
              fullWidth
              mt="md"
              onClick={() => navigate(feature.path)}
            >
              Get Started
            </Button>
          </Card>
        ))}
      </SimpleGrid>
    </Stack>
  );
};

export default HomePage;
