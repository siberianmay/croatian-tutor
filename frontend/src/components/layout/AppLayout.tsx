import React from 'react';
import { AppShell, Group, NavLink, Title, Container, Burger, useMantineTheme, Badge, Tooltip } from '@mantine/core';
import { useDisclosure, useMediaQuery } from '@mantine/hooks';
import { IconBook, IconVocabulary, IconPencil, IconChartBar, IconSchool, IconSettings, IconLanguage } from '@tabler/icons-react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useLanguage } from '~contexts/LanguageContext';

interface AppLayoutProps {
  children: React.ReactNode;
}

const navItems = [
  { label: 'Learn', path: '/', icon: IconBook },
  { label: 'Flashcards', path: '/flashcards', icon: IconPencil },
  { label: 'Vocabulary', path: '/vocabulary', icon: IconVocabulary },
  { label: 'Grammar', path: '/grammar', icon: IconSchool },
  { label: 'Progress', path: '/progress', icon: IconChartBar },
  { label: 'Settings', path: '/settings', icon: IconSettings },
];

export const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [opened, { toggle, close }] = useDisclosure();
  const theme = useMantineTheme();
  const isMobile = useMediaQuery(`(max-width: ${theme.breakpoints.sm})`);
  const { language } = useLanguage();

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
            <Title order={3}>{language?.name ?? 'Language'} Tutor</Title>
          </Group>
          <Tooltip label="Change language in Settings" position="bottom">
            <Badge
              size="lg"
              variant="light"
              color="blue"
              leftSection={<IconLanguage size={14} />}
              style={{ cursor: 'pointer' }}
              onClick={() => navigate('/settings')}
            >
              {language?.native_name ?? language?.name ?? 'Loading...'}
            </Badge>
          </Tooltip>
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
