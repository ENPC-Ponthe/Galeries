"""empty message

Revision ID: 84db0d5828df
Revises: fd02f1bc29c9
Create Date: 2018-10-14 14:56:18.578610

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '84db0d5828df'
down_revision = 'fd02f1bc29c9'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('galleries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('year_id', sa.Integer(), nullable=True),
        sa.Column('event_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], name='fk_galleries_event'),
        sa.ForeignKeyConstraint(['id'], ['resources.id'], onupdate='CASCADE', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['year_id'], ['years.id'], name='fk_galleries_year'),
        sa.PrimaryKeyConstraint('id')
    )
    op.add_column('files', sa.Column('gallery_id', sa.Integer(), nullable=False))
    op.drop_constraint('fk_files_event', 'files', type_='foreignkey')
    op.drop_constraint('fk_files_year', 'files', type_='foreignkey')
    op.create_foreign_key('fk_files_gallery', 'files', 'galleries', ['gallery_id'], ['id'])
    op.drop_column('files', 'event_id')
    op.drop_column('files', 'year_id')


def downgrade():
    op.add_column('files', sa.Column('year_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.add_column('files', sa.Column('event_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.drop_constraint('fk_files_gallery', 'files', type_='foreignkey')
    op.create_foreign_key('fk_files_year', 'files', 'years', ['year_id'], ['id'])
    op.create_foreign_key('fk_files_event', 'files', 'events', ['event_id'], ['id'])
    op.drop_column('files', 'gallery_id')
    op.drop_table('galleries')
