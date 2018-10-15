"""empty message

Revision ID: e452ec227bdf
Revises: f5a5f9bbd6e2
Create Date: 2018-04-22 13:50:27.284827

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'e452ec227bdf'
down_revision = 'f5a5f9bbd6e2'
branch_labels = None
depends_on = None


def upgrade():
    op.create_foreign_key(None, 'groups', 'resources', ['id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')


def downgrade():
    op.drop_constraint(None, 'groups', type_='foreignkey')
