"""Added required tables

Revision ID: 269b3412c0b7
Revises: 
Create Date: 2023-01-07 14:12:47.305908

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '269b3412c0b7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('email', sa.String(length=40), nullable=True),
                    sa.Column('name', sa.String(length=100), nullable=True),
                    sa.Column('hashed_password', sa.String(), nullable=True),
                    sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    op.create_table('tokens',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('token', postgresql.UUID(), nullable=False),
                    sa.Column('expires', sa.DateTime(), nullable=True),
                    sa.Column('user_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_tokens_token'), 'tokens', ['token'], unique=True)

    op.create_table('posts',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('user_id', sa.Integer(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('title', sa.String(length=100), nullable=True),
                    sa.Column('content', sa.Text(), nullable=True),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )

    op.create_table('like',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('like', sa.Boolean()),
                    sa.Column('post_id', sa.Integer(), nullable=True),
                    sa.Column('user_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('posts')
    op.drop_index(op.f('ix_tokens_token'), table_name='tokens')
    op.drop_table('tokens')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###
