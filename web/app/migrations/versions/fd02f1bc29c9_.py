"""empty message

Revision ID: fd02f1bc29c9
Revises: e452ec227bdf
Create Date: 2018-06-27 10:28:59.773364

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'fd02f1bc29c9'
down_revision = 'e452ec227bdf'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('events', sa.Column('description', sa.String(length=1024), nullable=True))
    op.alter_column('events', 'category_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)
    op.add_column('files', sa.Column('pending', sa.Boolean(), nullable=False))
    op.add_column('users', sa.Column('admin', sa.Boolean(), nullable=False))
    op.add_column('users', sa.Column('created', sa.DateTime(), nullable=False))
    op.add_column('users', sa.Column('email_confirmed', sa.Boolean(), nullable=False))


def downgrade():
    op.drop_column('users', 'email_confirmed')
    op.drop_column('users', 'created')
    op.drop_column('users', 'admin')
    op.drop_column('files', 'pending')
    op.alter_column('events', 'category_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)
    op.drop_column('events', 'description')
