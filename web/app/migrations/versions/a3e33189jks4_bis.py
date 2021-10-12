"""empty message

Revision ID: a3e33189jks4_bis
Revises: a3e33189jks4
Create Date: 2021-10-06 16:31:00.555331

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'a3e33189jks4_bis'
down_revision = 'a3e33189jks4'
branch_labels = None
depends_on = None


def upgrade():
    try:
        op.add_column('files', sa.Column(
            'date_time_original', sa.DateTime, nullable=False, server_default=sa.func.current_timestamp()))
    except Exception as e:
        print(e)
    try:
        op.add_column('files', sa.Column(
            'date_time_edited', sa.DateTime, nullable=False, server_default=sa.func.current_timestamp()))
    except Exception as e:
        print(e)


def downgrade():
    try:
        op.drop_column('files', 'date_time_original')
    except Exception as e:
        print(e)
    try:
        op.drop_column('files', 'date_time_edited')
    except Exception as e:
        print(e)
