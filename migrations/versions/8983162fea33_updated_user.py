"""updated User

Revision ID: 8983162fea33
Revises: f4df94d53ede
Create Date: 2023-05-17 18:22:21.212972

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8983162fea33'
down_revision = 'f4df94d53ede'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('email', sa.String(length=120), nullable=True))
    op.add_column('user', sa.Column('about_me', sa.String(length=140), nullable=True))
    op.add_column('user', sa.Column('last_seen', sa.DateTime(), nullable=True))
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_column('user', 'last_seen')
    op.drop_column('user', 'about_me')
    op.drop_column('user', 'email')
    # ### end Alembic commands ###