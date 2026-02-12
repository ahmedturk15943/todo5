"""Create full-text search trigger for tasks

Revision ID: 006_fulltext_search_trigger
Revises: 005_create_phase5_tables
Create Date: 2026-02-12

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '006_fulltext_search_trigger'
down_revision = '005_create_phase5_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create full-text search trigger for tasks table."""

    # Create trigger function to auto-update search_vector
    op.execute("""
        CREATE OR REPLACE FUNCTION tasks_search_vector_update() RETURNS trigger AS $$
        BEGIN
            NEW.search_vector :=
                setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
                setweight(to_tsvector('english', COALESCE(NEW.description, '')), 'B');
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create trigger to call function on INSERT or UPDATE
    op.execute("""
        CREATE TRIGGER tasks_search_vector_update_trigger
        BEFORE INSERT OR UPDATE ON tasks
        FOR EACH ROW
        EXECUTE FUNCTION tasks_search_vector_update();
    """)

    # Update existing rows to populate search_vector
    op.execute("""
        UPDATE tasks SET search_vector =
            setweight(to_tsvector('english', COALESCE(title, '')), 'A') ||
            setweight(to_tsvector('english', COALESCE(description, '')), 'B');
    """)


def downgrade() -> None:
    """Remove full-text search trigger."""
    # Drop trigger
    op.execute("DROP TRIGGER IF EXISTS tasks_search_vector_update_trigger ON tasks;")

    # Drop trigger function
    op.execute("DROP FUNCTION IF EXISTS tasks_search_vector_update();")
