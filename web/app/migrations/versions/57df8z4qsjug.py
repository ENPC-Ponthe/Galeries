"""empty message

Revision ID: 57df8z4qsjug
Revises: 221d1645dc18
Create Date: 2020-02-27 20:33:55.555331

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '57df8z4qsjug'
down_revision = '221d1645dc18'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('galleries', sa.Column('type', sa.Enum('PHOTO', 'VIDEO', 'MIXED', name='gallerytypeenum'), nullable=False))

def downgrade():
    op.drop_column('galleries', 'type')