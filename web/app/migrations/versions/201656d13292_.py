"""empty message

Revision ID: 201656d13292
Revises: 867456d02252
Create Date: 2018-10-15 00:13:32.126462

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '201656d13292'
down_revision = '867456d02252'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('galleries', sa.Column('description', sa.String(length=1024), nullable=True))
    op.add_column('galleries', sa.Column('cover_image_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_galleries_file', 'galleries', 'files', ['cover_image_id'], ['id'])

def downgrade():
    op.drop_column('galleries', 'description')
    op.drop_constraint('fk_galleries_file', 'galleries', type_='foreignkey')
    op.drop_column('galleries', 'cover_image_id')
