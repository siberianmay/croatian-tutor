import React from 'react';
import {
  Title,
  Text,
  Stack,
  Card,
  SimpleGrid,
  ThemeIcon,
  Button,
  Group,
  Badge,
} from '@mantine/core';
import {
  IconMessageCircle,
  IconBooks,
  IconLanguage,
  IconBlockquote,
  IconBook2,
  IconUsers,
} from '@tabler/icons-react';
import { useNavigate } from 'react-router-dom';

interface ExerciseCardProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  color: string;
  path: string;
  badge?: string;
}

const ExerciseCard: React.FC<ExerciseCardProps> = ({
  title,
  description,
  icon,
  color,
  path,
  badge,
}) => {
  const navigate = useNavigate();

  return (
    <Card shadow="sm" padding="lg" radius="md" withBorder>
      <Stack gap="md">
        <Group justify="space-between">
          <ThemeIcon size={50} radius="md" color={color}>
            {icon}
          </ThemeIcon>
          {badge && <Badge color={color}>{badge}</Badge>}
        </Group>
        <div>
          <Title order={4}>{title}</Title>
          <Text size="sm" c="dimmed" mt={4}>
            {description}
          </Text>
        </div>
        <Button
          variant="light"
          color={color}
          fullWidth
          onClick={() => navigate(path)}
        >
          Start
        </Button>
      </Stack>
    </Card>
  );
};

const LearnPage: React.FC = () => {
  return (
    <Stack gap="xl">
      <div>
        <Title order={1}>Learn Croatian</Title>
        <Text c="dimmed" mt="sm">
          Choose an exercise type to practice your Croatian skills
        </Text>
      </div>

      <SimpleGrid cols={{ base: 1, sm: 2, lg: 3 }} spacing="lg">
        <ExerciseCard
          title="Conversation"
          description="Chat freely with the AI tutor in Croatian. Get corrections and suggestions as you go."
          icon={<IconMessageCircle size={28} />}
          color="blue"
          path="/learn/conversation"
          badge="AI Tutor"
        />

        <ExerciseCard
          title="Grammar Exercises"
          description="Practice grammar topics like cases, conjugation, and sentence structure."
          icon={<IconBooks size={28} />}
          color="green"
          path="/learn/grammar"
        />

        <ExerciseCard
          title="Translation"
          description="Translate sentences between Croatian and English."
          icon={<IconLanguage size={28} />}
          color="orange"
          path="/learn/translation"
        />

        <ExerciseCard
          title="Sentence Construction"
          description="Arrange shuffled words to form correct Croatian sentences."
          icon={<IconBlockquote size={28} />}
          color="violet"
          path="/learn/sentence"
        />

        <ExerciseCard
          title="Reading Comprehension"
          description="Read Croatian passages and answer comprehension questions."
          icon={<IconBook2 size={28} />}
          color="teal"
          path="/learn/reading"
        />

        <ExerciseCard
          title="Dialogue Practice"
          description="Role-play real-world scenarios like ordering food or asking directions."
          icon={<IconUsers size={28} />}
          color="pink"
          path="/learn/dialogue"
        />
      </SimpleGrid>
    </Stack>
  );
};

export default LearnPage;
