import React from 'react';
import { Table, Skeleton, Stack } from '@mantine/core';

interface TableSkeletonProps {
  columns: number;
  rows?: number;
}

export const TableSkeleton: React.FC<TableSkeletonProps> = ({ columns, rows = 10 }) => {
  return (
    <Table striped>
      <Table.Thead>
        <Table.Tr>
          {Array.from({ length: columns }).map((_, i) => (
            <Table.Th key={i}>
              <Skeleton height={16} width={80} />
            </Table.Th>
          ))}
        </Table.Tr>
      </Table.Thead>
      <Table.Tbody>
        {Array.from({ length: rows }).map((_, rowIndex) => (
          <Table.Tr key={rowIndex}>
            {Array.from({ length: columns }).map((_, colIndex) => (
              <Table.Td key={colIndex}>
                <Skeleton height={14} width={colIndex === 0 ? 120 : 60 + Math.random() * 40} />
              </Table.Td>
            ))}
          </Table.Tr>
        ))}
      </Table.Tbody>
    </Table>
  );
};
