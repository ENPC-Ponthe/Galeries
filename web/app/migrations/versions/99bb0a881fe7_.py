"""empty message

Revision ID: 99bb0a881fe7
Revises: 221d1645dc18
Create Date: 2018-12-09 19:47:37.791706

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '99bb0a881fe7'
down_revision = '221d1645dc18'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('listes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('promotion', sa.String(length=64), nullable=False),
        sa.Column('type', sa.String(length=64), nullable=False),
        sa.Column('gallery_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['gallery_id'], ['galleries.id'], name='fk_liste_gallery'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('hotlines',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('phone', sa.String(length=10), nullable=True),
        sa.Column('image_url', sa.String(length=128), nullable=True),
        sa.Column('description', sa.String(length=1024), nullable=True),
        sa.Column('liste_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['liste_id'], ['listes.id'], name='fk_hotlines_liste'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('hotlines')
    op.drop_table('listes')
