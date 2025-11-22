import React from 'react';
import { Card, Skeleton, Stack } from '@mantine/core';

interface CardSkeletonProps {
  height?: number;
  lines?: number;
}

export const CardSkeleton: React.FC<CardSkeletonProps> = ({ height, lines = 3 }) => {
  return (
    <Card shadow="sm" padding="lg" radius="md" withBorder h={height}>
      <Stack gap="sm">
        <Skeleton height={20} width="60%" />
        {Array.from({ length: lines }).map((_, i) => (
          <Skeleton key={i} height={14} width={`${80 - i * 10}%`} />
        ))}
      </Stack>
    </Card>
  );
};
