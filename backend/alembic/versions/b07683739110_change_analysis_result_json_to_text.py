"""Change Analysis.result JSON to Text

Revision ID: b07683739110
Revises: 
Create Date: 2025-07-27 15:04:11.529414

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b07683739110'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column("analyses", "result", existing_type=sa.JSON(), type_=sa.Text())

def downgrade():
    op.alter_column("analyses", "result", existing_type=sa.Text(), type_=sa.JSON())

