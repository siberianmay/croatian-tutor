import { notifications } from '@mantine/notifications';
import { IconCheck, IconX, IconInfoCircle, IconAlertTriangle } from '@tabler/icons-react';
import { createElement } from 'react';

type NotificationColor = 'green' | 'red' | 'blue' | 'yellow';

interface ShowNotificationOptions {
  title?: string;
  message: string;
  autoClose?: number | false;
}

const showNotification = (
  color: NotificationColor,
  icon: typeof IconCheck,
  { title, message, autoClose = 4000 }: ShowNotificationOptions
): void => {
  notifications.show({
    title,
    message,
    color,
    icon: createElement(icon, { size: 18 }),
    autoClose,
  });
};

export const toast = {
  success: (message: string, title?: string): void => {
    showNotification('green', IconCheck, { title: title ?? 'Success', message });
  },

  error: (message: string, title?: string): void => {
    showNotification('red', IconX, { title: title ?? 'Error', message, autoClose: 6000 });
  },

  info: (message: string, title?: string): void => {
    showNotification('blue', IconInfoCircle, { title: title ?? 'Info', message });
  },

  warning: (message: string, title?: string): void => {
    showNotification('yellow', IconAlertTriangle, { title: title ?? 'Warning', message });
  },
};

export default toast;
