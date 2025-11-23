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
import { IconSend, IconArrowLeft, IconInfoCircle } from '@tabler/icons-react';
import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { exerciseApi } from '~services/exerciseApi';
import type { CEFRLevel, ConversationTurn } from '~types';

interface ChatMessage extends ConversationTurn {
  corrections?: Array<{
    original: string;
    corrected: string;
    explanation: string;
  }> | null;
  newVocabulary?: string[] | null;
}

const ConversationPage: React.FC = () => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [cefrLevel, setCefrLevel] = useState<CEFRLevel>('A1');
  const scrollRef = useRef<HTMLDivElement>(null);

  const conversationMutation = useMutation({
    mutationFn: (message: string) =>
      exerciseApi.conversation(
        {
          message,
          history: messages.map((m) => ({ role: m.role, content: m.content })),
        },
        cefrLevel
      ),
    onSuccess: (data) => {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.response,
          corrections: data.corrections,
          newVocabulary: data.new_vocabulary,
        },
      ]);
    },
  });

  useEffect(() => {
    // Scroll to bottom when messages change
    if (scrollRef.current) {
      scrollRef.current.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
    }
  }, [messages]);

  const handleSend = () => {
    if (!input.trim() || conversationMutation.isPending) return;

    const userMessage = input.trim();
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setInput('');
    conversationMutation.mutate(userMessage);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Stack gap="lg" style={{ height: 'calc(100vh - 140px)' }}>
      <Group justify="space-between">
        <Group>
          <ActionIcon variant="subtle" onClick={() => navigate('/learn')}>
            <IconArrowLeft size={20} />
          </ActionIcon>
          <div>
            <Title order={2}>Croatian Tutor</Title>
            <Text c="dimmed" size="sm">
              Practice conversational Croatian with AI
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

      {messages.length === 0 && (
        <Alert icon={<IconInfoCircle size={20} />} color="blue">
          <Text size="sm">
            Start a conversation in Croatian or English. The tutor will respond and correct
            any mistakes. Try: "Bok! Kako si?" or "Hello, I want to practice Croatian."
          </Text>
        </Alert>
      )}

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
              bg={msg.role === 'user' ? 'blue.0' : 'gray.0'}
              style={{
                alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                maxWidth: '80%',
              }}
            >
              <Stack gap="xs">
                <Text size="sm" fw={500} c={msg.role === 'user' ? 'blue.7' : 'gray.7'}>
                  {msg.role === 'user' ? 'You' : 'Tutor'}
                </Text>
                {msg.role === 'user' ? (
                  <Text>{msg.content}</Text>
                ) : (
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                )}

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
                        <Text size="xs" c="dimmed">
                          {c.explanation}
                        </Text>
                      </Stack>
                    ))}
                  </Card>
                )}

                {msg.newVocabulary && msg.newVocabulary.length > 0 && (
                  <Group gap={4}>
                    <Text size="xs" c="dimmed">
                      New words:
                    </Text>
                    {msg.newVocabulary.map((word, i) => (
                      <Badge key={i} size="sm" variant="outline" color="green">
                        {word}
                      </Badge>
                    ))}
                  </Group>
                )}
              </Stack>
            </Paper>
          ))}

          {conversationMutation.isPending && (
            <Paper p="md" radius="md" bg="gray.0" style={{ alignSelf: 'flex-start' }}>
              <Group gap="xs">
                <Loader size="xs" />
                <Text size="sm" c="dimmed">
                  Tutor is typing...
                </Text>
              </Group>
            </Paper>
          )}
        </Stack>
      </ScrollArea>

      <Group>
        <TextInput
          placeholder="Type your message in Croatian or English..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          flex={1}
          size="md"
          disabled={conversationMutation.isPending}
        />
        <Button
          onClick={handleSend}
          loading={conversationMutation.isPending}
          disabled={!input.trim()}
          size="md"
          leftSection={<IconSend size={18} />}
        >
          Send
        </Button>
      </Group>
    </Stack>
  );
};

export default ConversationPage;
