"""empty message

Revision ID: d44da88f0257
Revises: 8d9f85fb7f20
Create Date: 2022-09-10 21:31:28.866891

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd44da88f0257'
down_revision = '8d9f85fb7f20'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Shows', sa.Column('artist_id', sa.Integer(), nullable=False))
    op.add_column('Shows', sa.Column('venue_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'Shows', 'Artists', ['artist_id'], ['id'])
    op.create_foreign_key(None, 'Shows', 'Venues', ['venue_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'Shows', type_='foreignkey')
    op.drop_constraint(None, 'Shows', type_='foreignkey')
    op.drop_column('Shows', 'venue_id')
    op.drop_column('Shows', 'artist_id')
    # ### end Alembic commands ###
