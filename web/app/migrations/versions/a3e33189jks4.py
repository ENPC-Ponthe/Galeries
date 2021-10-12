"""empty message

Revision ID: a3e33189jks4
Revises: 57df8z4qsjug
Create Date: 2021-10-06 16:31:00.555331

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'a3e33189jks4'
down_revision = '57df8z4qsjug'
branch_labels = None
depends_on = None


def upgrade():
    try:
        op.add_column('files', sa.Column(
            'artist', sa.String(length=128), nullable=True))
    except Exception as e:
        print(e)
    try:
        op.add_column('files', sa.Column('camera_model',
                      sa.String(length=128), nullable=True))
    except Exception as e:
        print(e)
    try:
        op.add_column('files', sa.Column(
            'date_time_original', sa.DateTime(), nullable=False))
    except Exception as e:
        print(e)
    try:
        op.add_column('files', sa.Column(
            'date_time_edited', sa.DateTime(), nullable=False))
    except Exception as e:
        print(e)


def downgrade():
    try:
        op.drop_column('files', 'artist')
    except Exception as e:
        print(e)
    try:
        op.drop_column('files', 'camera_model')
    except Exception as e:
        print(e)
    try:
        op.drop_column('files', 'date_time_original')
    except Exception as e:
        print(e)
    try:
        op.drop_column('files', 'date_time_edited')
    except Exception as e:
        print(e)
