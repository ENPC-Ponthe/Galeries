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
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key('fk_categories_file', 'categories', 'files', ['cover_image_id'], ['id'])
    op.alter_column('events', 'private',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.Boolean(),
               existing_nullable=False)
    op.alter_column('users', 'password',
               existing_type=sa.String(length=64),
               type_=sa.Boolean(128),
               existing_nullable=False)
    op.create_foreign_key('fk_events_category', 'events', 'categories', ['category_id'], ['id'])
    op.create_foreign_key(None, 'groups', 'resources', ['id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'groups', type_='foreignkey')
    op.drop_constraint('fk_events_category', 'events', type_='foreignkey')
    op.alter_column('events', 'private',
               existing_type=sa.Boolean(),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=False)
    op.alter_column('users', 'password',
               existing_type=sa.String(length=128),
               type_=sa.Boolean(64),
               existing_nullable=False)
    op.drop_constraint('fk_categories_file', 'categories', type_='foreignkey')
    # ### end Alembic commands ###
