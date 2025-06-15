"""add tags and variables to prompt templates

Revision ID: 002
Revises: 001
Create Date: 2024-12-30 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    """Add tags, variables and usage_count columns to prompt_templates table"""
    
    # 添加tags列 (JSON类型)
    op.add_column('prompt_templates', sa.Column('tags', sa.JSON(), nullable=True))
    
    # 添加variables列 (JSON类型)
    op.add_column('prompt_templates', sa.Column('variables', sa.JSON(), nullable=True))
    
    # 添加usage_count列
    op.add_column('prompt_templates', sa.Column('usage_count', sa.Integer(), nullable=False, server_default='0'))


def downgrade():
    """Remove tags, variables and usage_count columns from prompt_templates table"""
    
    # 删除添加的列
    op.drop_column('prompt_templates', 'usage_count')
    op.drop_column('prompt_templates', 'variables')
    op.drop_column('prompt_templates', 'tags') 