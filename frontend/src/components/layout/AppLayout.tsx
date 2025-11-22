import React from 'react';
import { AppShell, Group, NavLink, Title, Container } from '@mantine/core';
import { IconHome, IconBook, IconPencil, IconChartBar } from '@tabler/icons-react';
import { useNavigate, useLocation } from 'react-router-dom';

interface AppLayoutProps {
  children: React.ReactNode;
}

const navItems = [
  { label: 'Home', path: '/', icon: IconHome },
  { label: 'Learn', path: '/learn', icon: IconBook },
  { label: 'Practice', path: '/practice', icon: IconPencil },
  { label: 'Progress', path: '/progress', icon: IconChartBar },
];

export const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <AppShell
      header={{ height: 60 }}
      navbar={{ width: 200, breakpoint: 'sm' }}
      padding="md"
    >
      <AppShell.Header>
        <Group h="100%" px="md">
          <Title order={3}>Croatian Tutor</Title>
        </Group>
      </AppShell.Header>

      <AppShell.Navbar p="md">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            label={item.label}
            leftSection={<item.icon size={16} />}
            active={location.pathname === item.path}
            onClick={() => navigate(item.path)}
          />
        ))}
      </AppShell.Navbar>

      <AppShell.Main>
        <Container size="lg">{children}</Container>
      </AppShell.Main>
    </AppShell>
  );
};
