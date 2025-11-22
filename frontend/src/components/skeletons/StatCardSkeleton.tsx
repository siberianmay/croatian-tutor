import React from 'react';
import { Card, Group, Skeleton, Stack } from '@mantine/core';

export const StatCardSkeleton: React.FC = () => {
  return (
    <Card shadow="sm" padding="lg" radius="md" withBorder>
      <Group justify="space-between" mb="xs">
        <Skeleton height={14} width={80} />
        <Skeleton height={32} width={32} circle />
      </Group>
      <Skeleton height={28} width={60} mt="sm" />
      <Skeleton height={12} width={100} mt="xs" />
    </Card>
  );
};
