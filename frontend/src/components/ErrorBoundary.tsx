import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Container, Title, Text, Button, Stack, Paper, Code } from '@mantine/core';
import { IconAlertTriangle, IconRefresh, IconHome } from '@tabler/icons-react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    this.setState({ errorInfo });
    // Log to console in development
    console.error('ErrorBoundary caught:', error, errorInfo);
  }

  handleReload = (): void => {
    window.location.reload();
  };

  handleGoHome = (): void => {
    window.location.href = '/';
  };

  handleReset = (): void => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  render(): ReactNode {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      const isDev = import.meta.env.DEV;

      return (
        <Container size="sm" py="xl">
          <Paper p="xl" radius="md" withBorder>
            <Stack align="center" gap="lg">
              <IconAlertTriangle size={64} color="var(--mantine-color-red-6)" />

              <Title order={2} ta="center">
                Something went wrong
              </Title>

              <Text c="dimmed" ta="center">
                An unexpected error occurred. You can try refreshing the page or returning to the home page.
              </Text>

              {isDev && this.state.error && (
                <Paper p="md" bg="gray.1" radius="sm" w="100%">
                  <Text size="sm" fw={600} mb="xs">
                    Error Details (dev only):
                  </Text>
                  <Code block>
                    {this.state.error.toString()}
                    {this.state.errorInfo?.componentStack && (
                      <>
                        {'\n\nComponent Stack:'}
                        {this.state.errorInfo.componentStack}
                      </>
                    )}
                  </Code>
                </Paper>
              )}

              <Stack gap="sm" w="100%">
                <Button
                  leftSection={<IconRefresh size={18} />}
                  onClick={this.handleReload}
                  fullWidth
                >
                  Refresh Page
                </Button>

                <Button
                  leftSection={<IconHome size={18} />}
                  variant="light"
                  onClick={this.handleGoHome}
                  fullWidth
                >
                  Go to Home
                </Button>

                <Button
                  variant="subtle"
                  onClick={this.handleReset}
                  fullWidth
                >
                  Try Again
                </Button>
              </Stack>
            </Stack>
          </Paper>
        </Container>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
