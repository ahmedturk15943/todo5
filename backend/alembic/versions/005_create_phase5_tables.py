"""Create Phase 5 tables

Revision ID: 005_create_phase5_tables
Revises: 004_extend_tasks_phase5
Create Date: 2026-02-12

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005_create_phase5_tables'
down_revision = '004_extend_tasks_phase5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create new Phase 5 tables."""

    # Create recurring_patterns table
    op.create_table(
        'recurring_patterns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('frequency', sa.String(length=20), nullable=False),
        sa.Column('interval', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('weekly_days', postgresql.JSON(), nullable=True),
        sa.Column('monthly_day', sa.Integer(), nullable=True),
        sa.Column('end_type', sa.String(length=20), nullable=False, server_default='never'),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('max_occurrences', sa.Integer(), nullable=True),
        sa.Column('current_occurrence', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.CheckConstraint('interval >= 1', name='chk_recurring_interval'),
        sa.CheckConstraint('monthly_day IS NULL OR (monthly_day >= 1 AND monthly_day <= 31)', name='chk_recurring_monthly_day'),
        sa.CheckConstraint('max_occurrences IS NULL OR max_occurrences >= 1', name='chk_recurring_max_occurrences'),
    )
    op.create_index('idx_recurring_patterns_user_id', 'recurring_patterns', ['user_id'])
    op.create_index('idx_recurring_patterns_frequency', 'recurring_patterns', ['frequency'])
    op.create_index('idx_recurring_patterns_start_date', 'recurring_patterns', ['start_date'])
    op.create_index('idx_recurring_patterns_is_active', 'recurring_patterns', ['is_active'])

    # Now add FK constraint from tasks to recurring_patterns
    op.create_foreign_key(
        'fk_tasks_recurring_pattern',
        'tasks', 'recurring_patterns',
        ['recurring_pattern_id'], ['id'],
        ondelete='SET NULL'
    )

    # Add self-referential FK for parent_task_id
    op.create_foreign_key(
        'fk_tasks_parent',
        'tasks', 'tasks',
        ['parent_task_id'], ['id'],
        ondelete='SET NULL'
    )

    # Create reminders table
    op.create_table(
        'reminders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('remind_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.String(length=500), nullable=True),
        sa.Column('job_id', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('job_id', name='uq_reminders_job_id'),
    )
    op.create_index('idx_reminders_task_id', 'reminders', ['task_id'])
    op.create_index('idx_reminders_user_id', 'reminders', ['user_id'])
    op.create_index('idx_reminders_remind_at', 'reminders', ['remind_at'])
    op.create_index('idx_reminders_status', 'reminders', ['status'])
    op.create_index('idx_reminders_pending', 'reminders', ['status', 'remind_at'], postgresql_where=sa.text("status = 'pending'"))

    # Create tags table
    op.create_table(
        'tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'name', name='uq_user_tag_name'),
    )
    op.create_index('idx_tags_user_id', 'tags', ['user_id'])
    op.create_index('idx_tags_name', 'tags', ['name'])

    # Create task_tags join table
    op.create_table(
        'task_tags',
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('task_id', 'tag_id'),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_task_tags_task_id', 'task_tags', ['task_id'])
    op.create_index('idx_task_tags_tag_id', 'task_tags', ['tag_id'])

    # Create activity_logs table
    op.create_table(
        'activity_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('activity_type', sa.String(length=30), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('changes', postgresql.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_activity_logs_task_id', 'activity_logs', ['task_id'])
    op.create_index('idx_activity_logs_user_id', 'activity_logs', ['user_id'])
    op.create_index('idx_activity_logs_timestamp', 'activity_logs', ['timestamp'])
    op.create_index('idx_activity_logs_type', 'activity_logs', ['activity_type'])
    op.create_index('idx_activity_logs_user_time', 'activity_logs', ['user_id', 'timestamp'])

    # Create notification_preferences table
    op.create_table(
        'notification_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('web_push_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('email_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('in_app_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('quiet_hours_start', sa.Integer(), nullable=True),
        sa.Column('quiet_hours_end', sa.Integer(), nullable=True),
        sa.Column('timezone', sa.String(length=50), nullable=False, server_default='UTC'),
        sa.Column('default_reminder_minutes', sa.Integer(), nullable=False, server_default='60'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', name='uq_notification_preferences_user_id'),
        sa.CheckConstraint(
            '(quiet_hours_start IS NULL AND quiet_hours_end IS NULL) OR (quiet_hours_start IS NOT NULL AND quiet_hours_end IS NOT NULL)',
            name='chk_notification_quiet_hours'
        ),
        sa.CheckConstraint('default_reminder_minutes >= 0', name='chk_notification_default_reminder'),
    )
    op.create_index('idx_notification_preferences_user_id', 'notification_preferences', ['user_id'])


def downgrade() -> None:
    """Drop Phase 5 tables."""
    # Drop tables in reverse order
    op.drop_table('notification_preferences')
    op.drop_table('activity_logs')
    op.drop_table('task_tags')
    op.drop_table('tags')
    op.drop_table('reminders')

    # Drop FK constraints from tasks
    op.drop_constraint('fk_tasks_parent', 'tasks', type_='foreignkey')
    op.drop_constraint('fk_tasks_recurring_pattern', 'tasks', type_='foreignkey')

    # Drop recurring_patterns table
    op.drop_table('recurring_patterns')
