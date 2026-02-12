"""Extend tasks table for Phase 5 features

Revision ID: 004_extend_tasks_phase5
Revises: 003_add_conversations_messages
Create Date: 2026-02-12

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004_extend_tasks_phase5'
down_revision = '003_add_conversations_messages'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add Phase 5 columns to tasks table."""
    # Add priority column
    op.add_column('tasks', sa.Column('priority', sa.String(length=10), nullable=False, server_default='medium'))

    # Add due_date column
    op.add_column('tasks', sa.Column('due_date', sa.DateTime(timezone=True), nullable=True))

    # Add recurring_pattern_id column (FK will be added after recurring_patterns table exists)
    op.add_column('tasks', sa.Column('recurring_pattern_id', sa.Integer(), nullable=True))

    # Add parent_task_id column (self-referential FK for recurring instances)
    op.add_column('tasks', sa.Column('parent_task_id', sa.Integer(), nullable=True))

    # Add version column for optimistic locking
    op.add_column('tasks', sa.Column('version', sa.Integer(), nullable=False, server_default='1'))

    # Add completed_at column
    op.add_column('tasks', sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True))

    # Add search_vector column for full-text search
    op.add_column('tasks', sa.Column('search_vector', postgresql.TSVECTOR(), nullable=True))

    # Rename 'completed' to 'status' for consistency
    # First add new status column
    op.add_column('tasks', sa.Column('status', sa.String(length=20), nullable=False, server_default='incomplete'))

    # Migrate data: completed=true -> status='complete', completed=false -> status='incomplete'
    op.execute("UPDATE tasks SET status = CASE WHEN completed = true THEN 'complete' ELSE 'incomplete' END")

    # Drop old completed column
    op.drop_column('tasks', 'completed')

    # Create indexes
    op.create_index('idx_tasks_priority', 'tasks', ['priority'])
    op.create_index('idx_tasks_due_date', 'tasks', ['due_date'])
    op.create_index('idx_tasks_status', 'tasks', ['status'])
    op.create_index('idx_tasks_user_priority', 'tasks', ['user_id', 'priority'])
    op.create_index('idx_tasks_user_due_date', 'tasks', ['user_id', 'due_date'])
    op.create_index('idx_tasks_search_vector', 'tasks', ['search_vector'], postgresql_using='gin')

    # Add check constraint for priority
    op.create_check_constraint(
        'chk_tasks_priority',
        'tasks',
        "priority IN ('high', 'medium', 'low')"
    )

    # Add check constraint for status
    op.create_check_constraint(
        'chk_tasks_status',
        'tasks',
        "status IN ('incomplete', 'complete')"
    )

    # Add check constraint for version
    op.create_check_constraint(
        'chk_tasks_version',
        'tasks',
        'version >= 1'
    )


def downgrade() -> None:
    """Remove Phase 5 columns from tasks table."""
    # Drop constraints
    op.drop_constraint('chk_tasks_version', 'tasks', type_='check')
    op.drop_constraint('chk_tasks_status', 'tasks', type_='check')
    op.drop_constraint('chk_tasks_priority', 'tasks', type_='check')

    # Drop indexes
    op.drop_index('idx_tasks_search_vector', 'tasks')
    op.drop_index('idx_tasks_user_due_date', 'tasks')
    op.drop_index('idx_tasks_user_priority', 'tasks')
    op.drop_index('idx_tasks_status', 'tasks')
    op.drop_index('idx_tasks_due_date', 'tasks')
    op.drop_index('idx_tasks_priority', 'tasks')

    # Add back completed column
    op.add_column('tasks', sa.Column('completed', sa.Boolean(), nullable=False, server_default='false'))

    # Migrate data back: status='complete' -> completed=true
    op.execute("UPDATE tasks SET completed = CASE WHEN status = 'complete' THEN true ELSE false END")

    # Drop new columns
    op.drop_column('tasks', 'status')
    op.drop_column('tasks', 'search_vector')
    op.drop_column('tasks', 'completed_at')
    op.drop_column('tasks', 'version')
    op.drop_column('tasks', 'parent_task_id')
    op.drop_column('tasks', 'recurring_pattern_id')
    op.drop_column('tasks', 'due_date')
    op.drop_column('tasks', 'priority')
