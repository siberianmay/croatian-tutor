import React, { useState } from 'react';
import {
  Title,
  Text,
  Stack,
  Table,
  Button,
  Group,
  Badge,
  ActionIcon,
  Modal,
  TextInput,
  Select,
  Loader,
  Center,
  Alert,
  Paper,
  Textarea,
} from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { IconPlus, IconPencil, IconTrash, IconSearch, IconUpload } from '@tabler/icons-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { wordApi } from '~services/wordApi';
import type { Word, WordCreate, WordUpdate, PartOfSpeech, Gender, CEFRLevel } from '~types';

const PART_OF_SPEECH_OPTIONS: { value: PartOfSpeech; label: string }[] = [
  { value: 'noun', label: 'Noun' },
  { value: 'verb', label: 'Verb' },
  { value: 'adjective', label: 'Adjective' },
  { value: 'adverb', label: 'Adverb' },
  { value: 'pronoun', label: 'Pronoun' },
  { value: 'preposition', label: 'Preposition' },
  { value: 'conjunction', label: 'Conjunction' },
  { value: 'phrase', label: 'Phrase' },
];

const GENDER_OPTIONS: { value: Gender; label: string }[] = [
  { value: 'masculine', label: 'Masculine' },
  { value: 'feminine', label: 'Feminine' },
  { value: 'neuter', label: 'Neuter' },
];

const CEFR_OPTIONS: { value: CEFRLevel; label: string }[] = [
  { value: 'A1', label: 'A1 - Beginner' },
  { value: 'A2', label: 'A2 - Elementary' },
  { value: 'B1', label: 'B1 - Intermediate' },
  { value: 'B2', label: 'B2 - Upper Intermediate' },
  { value: 'C1', label: 'C1 - Advanced' },
  { value: 'C2', label: 'C2 - Mastery' },
];

const getMasteryColor = (score: number): string => {
  if (score >= 8) return 'green';
  if (score >= 5) return 'yellow';
  if (score >= 2) return 'orange';
  return 'red';
};

interface WordFormData {
  croatian: string;
  english: string;
  part_of_speech: PartOfSpeech;
  gender: Gender | null;
  cefr_level: CEFRLevel;
}

const VocabularyPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [opened, { open, close }] = useDisclosure(false);
  const [bulkOpened, { open: openBulk, close: closeBulk }] = useDisclosure(false);
  const [editingWord, setEditingWord] = useState<Word | null>(null);
  const [search, setSearch] = useState('');
  const [bulkWords, setBulkWords] = useState('');
  const [bulkResult, setBulkResult] = useState<{ imported: number; skipped: number } | null>(null);
  const [formData, setFormData] = useState<WordFormData>({
    croatian: '',
    english: '',
    part_of_speech: 'noun',
    gender: null,
    cefr_level: 'A1',
  });

  const { data: words, isLoading, error } = useQuery({
    queryKey: ['words', search],
    queryFn: () => wordApi.list({ search: search || undefined, limit: 500 }),
  });

  const { data: dueCount } = useQuery({
    queryKey: ['words', 'due', 'count'],
    queryFn: () => wordApi.countDue(),
  });

  const createMutation = useMutation({
    mutationFn: (data: WordCreate) => wordApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['words'] });
      handleClose();
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: WordUpdate }) => wordApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['words'] });
      handleClose();
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => wordApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['words'] });
    },
  });

  const bulkImportMutation = useMutation({
    mutationFn: (words: string[]) => wordApi.bulkImport(words),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['words'] });
      setBulkResult({ imported: data.imported, skipped: data.skipped_duplicates });
      setBulkWords('');
    },
  });

  const handleBulkImport = () => {
    const words = bulkWords
      .split('\n')
      .map((w) => w.trim())
      .filter((w) => w.length > 0);
    if (words.length > 0) {
      bulkImportMutation.mutate(words);
    }
  };

  const handleCloseBulk = () => {
    closeBulk();
    setBulkResult(null);
  };

  const handleClose = () => {
    close();
    setEditingWord(null);
    setFormData({
      croatian: '',
      english: '',
      part_of_speech: 'noun',
      gender: null,
      cefr_level: 'A1',
    });
  };

  const handleEdit = (word: Word) => {
    setEditingWord(word);
    setFormData({
      croatian: word.croatian,
      english: word.english,
      part_of_speech: word.part_of_speech,
      gender: word.gender,
      cefr_level: word.cefr_level,
    });
    open();
  };

  const handleSubmit = () => {
    if (editingWord) {
      updateMutation.mutate({ id: editingWord.id, data: formData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const handleDelete = (word: Word) => {
    if (confirm(`Delete "${word.croatian}"?`)) {
      deleteMutation.mutate(word.id);
    }
  };

  if (error) {
    return (
      <Alert color="red" title="Error loading vocabulary">
        {(error as Error).message}
      </Alert>
    );
  }

  return (
    <Stack gap="lg">
      <div>
        <Title order={1}>Vocabulary</Title>
        <Text c="dimmed" mt="sm">
          Manage your Croatian vocabulary words
        </Text>
      </div>

      <Paper p="md" withBorder>
        <Group justify="space-between" mb="md">
          <Group>
            <TextInput
              placeholder="Search words..."
              leftSection={<IconSearch size={16} />}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ width: 250 }}
            />
            {dueCount !== undefined && dueCount > 0 && (
              <Badge color="orange" size="lg">
                {dueCount} words due for review
              </Badge>
            )}
          </Group>
          <Group>
            <Button variant="light" leftSection={<IconUpload size={16} />} onClick={openBulk}>
              Bulk Import
            </Button>
            <Button leftSection={<IconPlus size={16} />} onClick={open}>
              Add Word
            </Button>
          </Group>
        </Group>

        {isLoading ? (
          <Center py="xl">
            <Loader />
          </Center>
        ) : words && words.length > 0 ? (
          <Table striped highlightOnHover>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Croatian</Table.Th>
                <Table.Th>English</Table.Th>
                <Table.Th>Type</Table.Th>
                <Table.Th>Level</Table.Th>
                <Table.Th>Mastery</Table.Th>
                <Table.Th>Actions</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {words.map((word) => (
                <Table.Tr key={word.id}>
                  <Table.Td fw={500}>{word.croatian}</Table.Td>
                  <Table.Td>{word.english}</Table.Td>
                  <Table.Td>
                    <Badge variant="light" size="sm">
                      {word.part_of_speech}
                      {word.gender && ` (${word.gender.charAt(0)})`}
                    </Badge>
                  </Table.Td>
                  <Table.Td>
                    <Badge color="blue" variant="light" size="sm">
                      {word.cefr_level}
                    </Badge>
                  </Table.Td>
                  <Table.Td>
                    <Badge color={getMasteryColor(word.mastery_score)} size="sm">
                      {word.mastery_score}/10
                    </Badge>
                  </Table.Td>
                  <Table.Td>
                    <Group gap="xs">
                      <ActionIcon
                        variant="subtle"
                        color="blue"
                        onClick={() => handleEdit(word)}
                      >
                        <IconPencil size={16} />
                      </ActionIcon>
                      <ActionIcon
                        variant="subtle"
                        color="red"
                        onClick={() => handleDelete(word)}
                        loading={deleteMutation.isPending}
                      >
                        <IconTrash size={16} />
                      </ActionIcon>
                    </Group>
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        ) : (
          <Text c="dimmed" ta="center" py="xl">
            No words yet. Add your first word to get started!
          </Text>
        )}
      </Paper>

      <Modal
        opened={opened}
        onClose={handleClose}
        title={editingWord ? 'Edit Word' : 'Add Word'}
        size="md"
      >
        <Stack gap="md">
          <TextInput
            label="Croatian"
            placeholder="Enter Croatian word"
            required
            value={formData.croatian}
            onChange={(e) => setFormData({ ...formData, croatian: e.target.value })}
          />
          <TextInput
            label="English"
            placeholder="Enter English translation"
            required
            value={formData.english}
            onChange={(e) => setFormData({ ...formData, english: e.target.value })}
          />
          <Select
            label="Part of Speech"
            required
            data={PART_OF_SPEECH_OPTIONS}
            value={formData.part_of_speech}
            onChange={(value) =>
              setFormData({ ...formData, part_of_speech: value as PartOfSpeech })
            }
          />
          {formData.part_of_speech === 'noun' && (
            <Select
              label="Gender"
              data={GENDER_OPTIONS}
              value={formData.gender}
              onChange={(value) => setFormData({ ...formData, gender: value as Gender })}
              clearable
            />
          )}
          <Select
            label="CEFR Level"
            required
            data={CEFR_OPTIONS}
            value={formData.cefr_level}
            onChange={(value) => setFormData({ ...formData, cefr_level: value as CEFRLevel })}
          />
          <Group justify="flex-end" mt="md">
            <Button variant="subtle" onClick={handleClose}>
              Cancel
            </Button>
            <Button
              onClick={handleSubmit}
              loading={createMutation.isPending || updateMutation.isPending}
              disabled={!formData.croatian || !formData.english}
            >
              {editingWord ? 'Save' : 'Add'}
            </Button>
          </Group>
        </Stack>
      </Modal>

      <Modal
        opened={bulkOpened}
        onClose={handleCloseBulk}
        title="Bulk Import Words"
        size="lg"
      >
        <Stack gap="md">
          <Text size="sm" c="dimmed">
            Enter Croatian words (one per line). AI will automatically detect:
            English translation, part of speech, gender, and difficulty level.
          </Text>
          <Textarea
            placeholder="sunce&#10;mjesec&#10;zvijezda&#10;more&#10;planina"
            autosize
            minRows={20}
            value={bulkWords}
            onChange={(e) => setBulkWords(e.target.value)}
            disabled={bulkImportMutation.isPending}
          />
          {bulkResult && (
            <Alert color="green" title="Import Complete">
              Imported {bulkResult.imported} words.
              {bulkResult.skipped > 0 && ` Skipped ${bulkResult.skipped} duplicates.`}
            </Alert>
          )}
          {bulkImportMutation.isError && (
            <Alert color="red" title="Import Failed">
              {(bulkImportMutation.error as Error).message}
            </Alert>
          )}
          <Group justify="flex-end" mt="md">
            <Button variant="subtle" onClick={handleCloseBulk}>
              {bulkResult ? 'Close' : 'Cancel'}
            </Button>
            {!bulkResult && (
              <Button
                onClick={handleBulkImport}
                loading={bulkImportMutation.isPending}
                disabled={!bulkWords.trim()}
              >
                Import with AI
              </Button>
            )}
          </Group>
        </Stack>
      </Modal>
    </Stack>
  );
};

export default VocabularyPage;
