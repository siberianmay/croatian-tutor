import React, { useState, useRef, useEffect } from 'react';
import {
  Title,
  Text,
  Stack,
  Card,
  TextInput,
  Button,
  Paper,
  ScrollArea,
  Group,
  Badge,
  Alert,
  Select,
  ActionIcon,
  Loader,
} from '@mantine/core';
import { IconSend, IconArrowLeft, IconRefresh, IconInfoCircle } from '@tabler/icons-react';
import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { exerciseApi } from '~services/exerciseApi';
import type { CEFRLevel, DialogueExerciseResponse, ConversationTurn } from '~types';

interface ChatMessage extends ConversationTurn {
  corrections?: Array<{
    original: string;
    corrected: string;
    explanation: string;
  }> | null;
}

const DialoguePage: React.FC = () => {
  const navigate = useNavigate();
  const [cefrLevel, setCefrLevel] = useState<CEFRLevel>('A1');
  const [scenario, setScenario] = useState<DialogueExerciseResponse | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);

  // End chat session when leaving the page
  useEffect(() => {
    return () => {
      exerciseApi.endSession('dialogue').catch(() => {});
    };
  }, []);

  const generateMutation = useMutation({
    mutationFn: () => exerciseApi.generateDialogue({ cefr_level: cefrLevel }),
    onSuccess: (data) => {
      setScenario(data);
      setMessages([{ role: 'assistant', content: data.dialogue_start }]);
      setInput('');
    },
  });

  const dialogueMutation = useMutation({
    mutationFn: (message: string) =>
      exerciseApi.dialogueTurn(
        scenario?.exercise_id || '',
        message,
        scenario?.ai_role || '',
        scenario?.scenario || '',
        messages.map((m) => ({ role: m.role, content: m.content })),
        cefrLevel
      ),
    onSuccess: (data) => {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.response,
          corrections: data.corrections,
        },
      ]);
    },
  });

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
    }
  }, [messages]);

  const handleSend = () => {
    if (!input.trim() || dialogueMutation.isPending) return;

    const userMessage = input.trim();
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setInput('');
    dialogueMutation.mutate(userMessage);
  };

  return (
    <Stack gap="lg" style={{ height: 'calc(100vh - 140px)' }}>
      <Group justify="space-between">
        <Group>
          <ActionIcon variant="subtle" onClick={() => navigate('/')}>
            <IconArrowLeft size={20} />
          </ActionIcon>
          <div>
            <Title order={2}>Dialogue Practice</Title>
            <Text c="dimmed" size="sm">
              Role-play real-world scenarios
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

      {!scenario ? (
        <Card shadow="sm" padding="xl" radius="md" withBorder flex={1}>
          <Stack align="center" justify="center" h="100%" gap="lg">
            <Text size="lg">Practice conversations in real-world scenarios</Text>
            <Text c="dimmed" ta="center" maw={400}>
              You'll be assigned a role and engage in a dialogue with an AI partner.
              Great for practicing ordering food, asking directions, shopping, and more!
            </Text>
            <Button
              size="lg"
              onClick={() => generateMutation.mutate()}
              loading={generateMutation.isPending}
              leftSection={<IconRefresh size={20} />}
            >
              Start Dialogue
            </Button>
          </Stack>
        </Card>
      ) : (
        <>
          {/* Scenario Info */}
          <Card shadow="sm" padding="md" radius="md" withBorder>
            <Group justify="space-between">
              <Stack gap={4}>
                <Text fw={600}>{scenario.scenario}</Text>
                <Group gap="xs">
                  <Badge color="blue">You: {scenario.user_role}</Badge>
                  <Badge color="pink">AI: {scenario.ai_role}</Badge>
                </Group>
              </Stack>
              <Button
                variant="subtle"
                size="xs"
                onClick={() => generateMutation.mutate()}
                loading={generateMutation.isPending}
              >
                New Scenario
              </Button>
            </Group>
          </Card>

          {/* Suggested Phrases */}
          {scenario.suggested_phrases.length > 0 && (
            <Alert icon={<IconInfoCircle size={16} />} color="blue" p="xs">
              <Text size="xs" fw={500} mb={4}>
                Useful phrases:
              </Text>
              <Group gap={4}>
                {scenario.suggested_phrases.map((phrase, i) => (
                  <Badge key={i} size="sm" variant="outline">
                    {phrase}
                  </Badge>
                ))}
              </Group>
            </Alert>
          )}

          {/* Chat */}
          <ScrollArea
            flex={1}
            viewportRef={scrollRef}
            style={{ border: '1px solid var(--mantine-color-gray-3)', borderRadius: 8 }}
            p="md"
          >
            <Stack gap="md">
              {messages.map((msg, idx) => (
                <Paper
                  key={idx}
                  p="md"
                  radius="md"
                  bg={msg.role === 'user' ? 'blue.0' : 'pink.0'}
                  style={{
                    alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                    maxWidth: '80%',
                  }}
                >
                  <Stack gap="xs">
                    <Text size="sm" fw={500} c={msg.role === 'user' ? 'blue.7' : 'pink.7'}>
                      {msg.role === 'user' ? scenario.user_role : scenario.ai_role}
                    </Text>
                    <Text>{msg.content}</Text>

                    {msg.corrections && msg.corrections.length > 0 && (
                      <Card withBorder p="sm" bg="yellow.0" radius="sm">
                        <Text size="xs" fw={600} c="yellow.8" mb={4}>
                          Corrections:
                        </Text>
                        {msg.corrections.map((c, i) => (
                          <Stack key={i} gap={2}>
                            <Text size="xs" c="red.6" style={{ textDecoration: 'line-through' }}>
                              {c.original}
                            </Text>
                            <Text size="xs" c="green.7" fw={500}>
                              {c.corrected}
                            </Text>
                          </Stack>
                        ))}
                      </Card>
                    )}
                  </Stack>
                </Paper>
              ))}

              {dialogueMutation.isPending && (
                <Paper p="md" radius="md" bg="pink.0" style={{ alignSelf: 'flex-start' }}>
                  <Group gap="xs">
                    <Loader size="xs" />
                    <Text size="sm" c="dimmed">
                      {scenario.ai_role} is responding...
                    </Text>
                  </Group>
                </Paper>
              )}
            </Stack>
          </ScrollArea>

          {/* Input */}
          <Group>
            <TextInput
              placeholder={`Respond as ${scenario.user_role}...`}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              flex={1}
              size="md"
              disabled={dialogueMutation.isPending}
            />
            <Button
              onClick={handleSend}
              loading={dialogueMutation.isPending}
              disabled={!input.trim()}
              size="md"
              leftSection={<IconSend size={18} />}
            >
              Send
            </Button>
          </Group>
        </>
      )}
    </Stack>
  );
};

export default DialoguePage;
