"""add git platform config tables

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建Git平台配置表
    op.create_table('git_platform_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('platform', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('encrypted_token', sa.String(), nullable=False),
        sa.Column('base_url', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_git_platform_configs_name'), 'git_platform_configs', ['name'], unique=False)
    op.create_index(op.f('ix_git_platform_configs_id'), 'git_platform_configs', ['id'], unique=False)

    # 如果仓库表存在，添加platform_config_id字段
    try:
        op.add_column('repositories', sa.Column('platform_config_id', sa.Integer(), nullable=True))
        op.create_foreign_key('fk_repositories_platform_config', 'repositories', 'git_platform_configs', ['platform_config_id'], ['id'])
    except Exception:
        # 如果表不存在，创建完整的仓库表
        op.create_table('repositories',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('alias', sa.String(), nullable=False),
            sa.Column('url', sa.String(), nullable=False),
            sa.Column('default_base_branch', sa.String(), nullable=True, default='main'),
            sa.Column('description', sa.String(), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
            sa.Column('platform_config_id', sa.Integer(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['platform_config_id'], ['git_platform_configs.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_repositories_alias'), 'repositories', ['alias'], unique=False)
        op.create_index(op.f('ix_repositories_id'), 'repositories', ['id'], unique=False)


def downgrade() -> None:
    # 删除外键约束和字段
    try:
        op.drop_constraint('fk_repositories_platform_config', 'repositories', type_='foreignkey')
        op.drop_column('repositories', 'platform_config_id')
    except Exception:
        pass
    
    # 删除Git平台配置表
    op.drop_index(op.f('ix_git_platform_configs_name'), table_name='git_platform_configs')
    op.drop_index(op.f('ix_git_platform_configs_id'), table_name='git_platform_configs')
    op.drop_table('git_platform_configs') 