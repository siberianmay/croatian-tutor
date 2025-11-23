import React from 'react';
import { AppShell, Group, NavLink, Title, Container, Burger, useMantineTheme } from '@mantine/core';
import { useDisclosure, useMediaQuery } from '@mantine/hooks';
import { IconBook, IconVocabulary, IconPencil, IconChartBar, IconSchool } from '@tabler/icons-react';
import { useNavigate, useLocation } from 'react-router-dom';

interface AppLayoutProps {
  children: React.ReactNode;
}

const navItems = [
  { label: 'Learn', path: '/', icon: IconBook },
  { label: 'Vocabulary', path: '/vocabulary', icon: IconVocabulary },
  { label: 'Grammar', path: '/grammar', icon: IconSchool },
  { label: 'Practice', path: '/practice', icon: IconPencil },
  { label: 'Progress', path: '/progress', icon: IconChartBar },
];

export const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [opened, { toggle, close }] = useDisclosure();
  const theme = useMantineTheme();
  const isMobile = useMediaQuery(`(max-width: ${theme.breakpoints.sm})`);

  const handleNavClick = (path: string) => {
    navigate(path);
    if (isMobile) {
      close();
    }
  };

  return (
    <AppShell
      header={{ height: 60 }}
      navbar={{
        width: 200,
        breakpoint: 'sm',
        collapsed: { mobile: !opened },
      }}
      padding="md"
    >
      <AppShell.Header>
        <Group h="100%" px="md" justify="space-between">
          <Group>
            <Burger
              opened={opened}
              onClick={toggle}
              hiddenFrom="sm"
              size="sm"
            />
            <Title order={3}>Croatian Tutor</Title>
          </Group>
        </Group>
      </AppShell.Header>

      <AppShell.Navbar p="md">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            label={item.label}
            leftSection={<item.icon size={16} />}
            active={location.pathname === item.path}
            onClick={() => handleNavClick(item.path)}
          />
        ))}
      </AppShell.Navbar>

      <AppShell.Main>
        <Container size="lg">{children}</Container>
      </AppShell.Main>
    </AppShell>
  );
};
