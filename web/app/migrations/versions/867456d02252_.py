"""empty message

Revision ID: 867456d02252
Revises: 84db0d5828df
Create Date: 2018-10-14 16:54:32.126462

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '867456d02252'
down_revision = '84db0d5828df'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('events', 'private')
    op.add_column('files', sa.Column('extension', sa.String(length=64), nullable=True))
    op.drop_index('filename', table_name='files')
    op.drop_column('files', 'filename')
    op.add_column('galleries', sa.Column('private', sa.Boolean(), nullable=False))
    op.add_column('groups', sa.Column('gallery_id', sa.Integer(), nullable=True))
    op.drop_constraint('fk_groups_event', 'groups', type_='foreignkey')
    op.drop_constraint('fk_groups_year', 'groups', type_='foreignkey')
    op.create_foreign_key('fk_groups_gallery', 'groups', 'galleries', ['gallery_id'], ['id'])
    op.drop_column('groups', 'year_id')
    op.drop_column('groups', 'event_id')


def downgrade():
    op.add_column('groups', sa.Column('event_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.add_column('groups', sa.Column('year_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.drop_constraint('fk_groups_gallery', 'groups', type_='foreignkey')
    op.create_foreign_key('fk_groups_year', 'groups', 'years', ['year_id'], ['id'])
    op.create_foreign_key('fk_groups_event', 'groups', 'events', ['event_id'], ['id'])
    op.drop_column('groups', 'gallery_id')
    op.drop_column('galleries', 'private')
    op.add_column('files', sa.Column('filename', mysql.VARCHAR(length=64), nullable=False))
    op.create_index('filename', 'files', ['filename'], unique=True)
    op.drop_column('files', 'extension')
    op.add_column('events', sa.Column('private', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False))
    # ### end Alembic commands ###
