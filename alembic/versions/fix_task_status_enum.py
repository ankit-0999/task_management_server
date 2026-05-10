"""Fix task status enum values to match code

Revision ID: fix_task_status_enum
Revises: c70ac89a3caf
Create Date: 2026-05-10 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fix_task_status_enum'
down_revision: Union[str, Sequence[str], None] = 'c70ac89a3caf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create a new enum type with all values (old and new)
    op.execute("CREATE TYPE taskstatus_new AS ENUM ('TODO', 'IN_PROGRESS', 'COMPLETED', 'OVERDUE', 'Todo', 'In-Progress', 'Completed', 'Overdue', 'On-Hold')")
    
    # Cast the column to the new type
    op.execute("ALTER TABLE tasks ALTER COLUMN status TYPE taskstatus_new USING status::text::taskstatus_new")
    
    # Update data to new values
    op.execute("UPDATE tasks SET status = 'Todo' WHERE status = 'TODO'")
    op.execute("UPDATE tasks SET status = 'In-Progress' WHERE status = 'IN_PROGRESS'")
    op.execute("UPDATE tasks SET status = 'Completed' WHERE status = 'COMPLETED'")
    op.execute("UPDATE tasks SET status = 'Overdue' WHERE status = 'OVERDUE'")
    
    # Drop the old enum and rename the new one
    op.execute("DROP TYPE taskstatus")
    op.execute("ALTER TYPE taskstatus_new RENAME TO taskstatus")
    
    # Set the default
    op.execute("ALTER TABLE tasks ALTER COLUMN status SET DEFAULT 'Todo'::taskstatus")


def downgrade() -> None:
    """Downgrade schema."""
    # Create the old enum type
    op.execute("CREATE TYPE taskstatus_old AS ENUM ('TODO', 'IN_PROGRESS', 'COMPLETED', 'OVERDUE')")
    
    # Update data back to old values
    op.execute("UPDATE tasks SET status = 'TODO' WHERE status = 'Todo'")
    op.execute("UPDATE tasks SET status = 'IN_PROGRESS' WHERE status = 'In-Progress'")
    op.execute("UPDATE tasks SET status = 'COMPLETED' WHERE status = 'Completed'")
    op.execute("UPDATE tasks SET status = 'Overdue' WHERE status = 'OVERDUE'")
    
    # Cast back to old enum
    op.execute("ALTER TABLE tasks ALTER COLUMN status TYPE taskstatus_old USING status::text::taskstatus_old")
    
    # Drop the new enum and rename the old one
    op.execute("DROP TYPE taskstatus")
    op.execute("ALTER TYPE taskstatus_old RENAME TO taskstatus")
    
    # Set the default back
    op.execute("ALTER TABLE tasks ALTER COLUMN status SET DEFAULT 'TODO'::taskstatus")
