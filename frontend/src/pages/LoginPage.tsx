import React, { useState } from 'react';
import {
  Container,
  Title,
  Text,
  Paper,
  TextInput,
  PasswordInput,
  Button,
  Group,
  Anchor,
  Stack,
  Alert,
  Divider,
} from '@mantine/core';
import { IconAlertCircle, IconLanguage } from '@tabler/icons-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '~contexts/AuthContext';
import type { AxiosError } from 'axios';

interface ApiError {
  detail: string;
}

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login, register } = useAuth();

  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [name, setName] = useState('');
  const [referralCode, setReferralCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (isRegister && password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    setIsLoading(true);

    try {
      if (isRegister) {
        await register({ email, password, name: name || undefined, referral_code: referralCode });
      } else {
        await login({ email, password });
      }
      navigate('/');
    } catch (err) {
      const axiosError = err as AxiosError<ApiError>;
      const message = axiosError.response?.data?.detail || 'An error occurred. Please try again.';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleMode = () => {
    setIsRegister(!isRegister);
    setError(null);
    setConfirmPassword('');
    setReferralCode('');
  };

  return (
    <Container size={420} my={40}>
      <Stack align="center" mb="xl">
        <IconLanguage size={48} stroke={1.5} color="var(--mantine-color-blue-6)" />
        <Title ta="center">
          Language Tutor
        </Title>
        <Text c="dimmed" size="sm" ta="center">
          {isRegister
            ? 'Create an account to start learning'
            : 'Sign in to continue learning'}
        </Text>
      </Stack>

      <Paper withBorder shadow="md" p={30} radius="md">
        <form onSubmit={handleSubmit}>
          <Stack gap="md">
            {error && (
              <Alert color="red" icon={<IconAlertCircle size={16} />} title="Error">
                {error}
              </Alert>
            )}

            {isRegister && (
              <TextInput
                label="Name"
                placeholder="Your name (optional)"
                value={name}
                onChange={(e) => setName(e.currentTarget.value)}
              />
            )}

            <TextInput
              label="Email"
              placeholder="you@example.com"
              required
              value={email}
              onChange={(e) => setEmail(e.currentTarget.value)}
              type="email"
            />

            <PasswordInput
              label="Password"
              placeholder="Your password"
              required
              value={password}
              onChange={(e) => setPassword(e.currentTarget.value)}
              description={isRegister ? 'At least 8 characters' : undefined}
            />

            {isRegister && (
              <PasswordInput
                label="Confirm Password"
                placeholder="Confirm your password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.currentTarget.value)}
              />
            )}

            {isRegister && (
              <TextInput
                label="Referral Code"
                placeholder="Enter your referral code"
                required
                value={referralCode}
                onChange={(e) => setReferralCode(e.currentTarget.value)}
              />
            )}

            <Button type="submit" fullWidth mt="md" loading={isLoading}>
              {isRegister ? 'Create Account' : 'Sign In'}
            </Button>
          </Stack>
        </form>

        <Divider my="lg" />

        <Group justify="center">
          <Text size="sm" c="dimmed">
            {isRegister ? 'Already have an account?' : "Don't have an account?"}
          </Text>
          <Anchor component="button" size="sm" onClick={toggleMode}>
            {isRegister ? 'Sign in' : 'Register'}
          </Anchor>
        </Group>
      </Paper>
    </Container>
  );
};

export default LoginPage;
