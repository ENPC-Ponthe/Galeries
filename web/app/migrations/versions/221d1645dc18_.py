"""empty message

Revision ID: 221d1645dc18
Revises: 201656d13292
Create Date: 2018-10-15 21:33:55.555331

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '221d1645dc18'
down_revision = '201656d13292'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('department', sa.String(length=64), nullable=True))
    op.add_column('users', sa.Column('gender', sa.Enum('M', 'F', name='genderenum'), nullable=True))
    op.add_column('users', sa.Column('origin', sa.String(length=64), nullable=True))
    op.add_column('users', sa.Column('promotion', sa.String(length=64), nullable=True))
    op.add_column('years', sa.Column('description', sa.String(length=1024), nullable=True))


def downgrade():
    op.drop_column('years', 'description')
    op.drop_column('users', 'promotion')
    op.drop_column('users', 'origin')
    op.drop_column('users', 'gender')
    op.drop_column('users', 'department')
