"""Recurring task types."""

export interface RecurringPattern {
  id: number;
  user_id: string;
  frequency: 'daily' | 'weekly' | 'monthly' | 'custom';
  interval: number;
  start_date: string;
  weekly_days?: number[];
  monthly_day?: number;
  end_type: 'never' | 'after_occurrences' | 'by_date';
  end_date?: string;
  max_occurrences?: number;
  current_occurrence: number;
  created_at: string;
  is_active: boolean;
}

export interface RecurringPatternCreate {
  frequency: 'daily' | 'weekly' | 'monthly' | 'custom';
  interval: number;
  start_date: string;
  weekly_days?: number[];
  monthly_day?: number;
  end_type: 'never' | 'after_occurrences' | 'by_date';
  end_date?: string;
  max_occurrences?: number;
}
