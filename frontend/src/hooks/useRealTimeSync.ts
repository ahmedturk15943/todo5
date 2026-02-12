"""useRealTimeSync hook for real-time task synchronization."""

import { useEffect } from 'react';
import { useWebSocket } from './useWebSocket';

interface Task {
  id: number;
  [key: string]: any;
}

export function useRealTimeSync(
  userId: string | undefined,
  onTaskUpdate: (task: Task) => void,
  onTaskDelete: (taskId: number) => void
) {
  const { connected, subscribe, unsubscribe } = useWebSocket(userId);

  useEffect(() => {
    if (!connected) return;

    const handleTaskUpdate = (data: any) => {
      const { event_type, task_id, changes } = data;

      if (event_type === 'task.created' || event_type === 'task.updated') {
        onTaskUpdate(changes);
      } else if (event_type === 'task.deleted') {
        onTaskDelete(task_id);
      }
    };

    subscribe('task_update', handleTaskUpdate);

    return () => {
      unsubscribe('task_update', handleTaskUpdate);
    };
  }, [connected, onTaskUpdate, onTaskDelete]);

  return { connected };
}
