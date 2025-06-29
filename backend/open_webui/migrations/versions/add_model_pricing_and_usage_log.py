"""Add model_pricing and usage_log tables

Revision ID: aipro_token_cost_usage
Revises: 1af9b942657b
Create Date: 2024-06-10

"""

from alembic import op
import sqlalchemy as sa

revision = 'aipro_token_cost_usage'
down_revision = '1af9b942657b'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'model_pricing',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('model_id', sa.String(), nullable=False, index=True),
        sa.Column('auto_pricing', sa.Float, nullable=True),
        sa.Column('manual_price', sa.Float, nullable=True),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('updated_at', sa.BigInteger, nullable=False),
        sa.UniqueConstraint('model_id', name='uq_model_pricing_model_id'),
    )

    op.create_table(
        'usage_log',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.String(), nullable=False, index=True),
        sa.Column('model', sa.String(), nullable=False),
        sa.Column('tokens_prompt', sa.Integer, nullable=False),
        sa.Column('tokens_completion', sa.Integer, nullable=False),
        sa.Column('cost', sa.Float, nullable=False),
        sa.Column('timestamp', sa.BigInteger, nullable=False),
        sa.Column('conversation_id', sa.String(), nullable=True, index=True),
    )

def downgrade():
    op.drop_table('usage_log')
    op.drop_table('model_pricing') 