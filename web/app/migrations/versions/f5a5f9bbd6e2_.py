"""empty message

Revision ID: f5a5f9bbd6e2
Revises: 2aba59ed46f8
Create Date: 2018-04-20 19:02:32.403757

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f5a5f9bbd6e2'
down_revision = '2aba59ed46f8'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('categories', sa.Column('cover_image_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_categories_file', 'categories', 'files', ['cover_image_id'], ['id'])
    op.add_column('events', sa.Column('cover_image_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_events_file', 'events', 'files', ['cover_image_id'], ['id'])
    op.add_column('groups', sa.Column('event_id', sa.Integer(), nullable=True))
    op.add_column('groups', sa.Column('year_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_groups_event', 'groups', 'events', ['event_id'], ['id'])
    op.create_foreign_key('fk_groups_year', 'groups', 'years', ['year_id'], ['id'])
    op.add_column('years', sa.Column('cover_image_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_years_file', 'years', 'files', ['cover_image_id'], ['id'])


def downgrade():
    op.drop_constraint('fk_years_file', 'years', type_='foreignkey')
    op.drop_column('years', 'cover_image_id')
    op.drop_constraint('fk_groups_event', 'groups', type_='foreignkey')
    op.drop_constraint('fk_groups_year', 'groups', type_='foreignkey')
    op.drop_column('groups', 'year_id')
    op.drop_column('groups', 'event_id')
    op.drop_constraint('fk_events_file', 'events', type_='foreignkey')
    op.drop_column('events', 'cover_image_id')
    op.drop_constraint('fk_categories_file', 'categories', type_='foreignkey')
    op.drop_column('categories', 'cover_image_id')
