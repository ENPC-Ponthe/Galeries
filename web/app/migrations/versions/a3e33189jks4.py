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
    op.add_column('files', sa.Column('artist', sa.String(length=128), nullable=True))
    op.add_column('files', sa.Column('camera_model', sa.String(length=128), nullable=True))
    op.add_column('files', sa.Column('date_time_original', sa.DateTime(), nullable=False))
    op.add_column('files', sa.Column('date_time_edited', sa.String(), nullable=False))


def downgrade():
    op.drop_column('files', 'artist')
    op.drop_column('files', 'camera_model')
    op.drop_column('files', 'date_time_original')
    op.drop_column('files', 'date_time_edited')
