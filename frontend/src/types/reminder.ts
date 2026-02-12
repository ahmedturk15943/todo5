"""Reminder types."""

export interface Reminder {
  id: number;
  task_id: number;
  user_id: string;
  remind_at: string;
  created_at: string;
  status: 'pending' | 'sent' | 'cancelled' | 'failed';
  sent_at?: string;
  job_id?: string;
}

export interface ReminderCreate {
  task_id: number;
  remind_at: string;
}
