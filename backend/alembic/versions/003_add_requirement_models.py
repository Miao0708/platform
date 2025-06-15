"""add requirement document and task models

Revision ID: 003
Revises: 002
Create Date: 2024-12-30 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    """Add requirement document and task tables"""
    
    # 创建需求文档表
    op.create_table('requirement_documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('original_content', sa.Text(), nullable=False),
        sa.Column('optimized_content', sa.Text(), nullable=True),
        sa.Column('source', sa.String(), nullable=False),
        sa.Column('original_filename', sa.String(), nullable=True),
        sa.Column('file_type', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('prompt_template_id', sa.Integer(), nullable=True),
        sa.Column('model_config_id', sa.Integer(), nullable=True),
        sa.Column('parse_task_id', sa.String(), nullable=True),
        sa.Column('error_message', sa.String(), nullable=True),
        sa.Column('task_started_at', sa.String(), nullable=True),
        sa.Column('task_completed_at', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建需求分析任务表
    op.create_table('requirement_analysis_tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('requirement_document_id', sa.Integer(), nullable=False),
        sa.Column('prompt_template_id', sa.Integer(), nullable=False),
        sa.Column('model_config_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('result', sa.Text(), nullable=True),
        sa.Column('error_message', sa.String(), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('execution_time', sa.Float(), nullable=True),
        sa.Column('started_at', sa.String(), nullable=True),
        sa.Column('completed_at', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建需求测试分析任务表
    op.create_table('requirement_test_tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('requirement_id', sa.Integer(), nullable=True),
        sa.Column('requirement_content', sa.Text(), nullable=True),
        sa.Column('prompt_template_id', sa.Integer(), nullable=False),
        sa.Column('model_config_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('result', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.String(), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('execution_time', sa.Float(), nullable=True),
        sa.Column('started_at', sa.String(), nullable=True),
        sa.Column('completed_at', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建索引
    op.create_index('ix_requirement_documents_status', 'requirement_documents', ['status'])
    op.create_index('ix_requirement_analysis_tasks_status', 'requirement_analysis_tasks', ['status'])
    op.create_index('ix_requirement_test_tasks_status', 'requirement_test_tasks', ['status'])


def downgrade():
    """Remove requirement document and task tables"""
    
    # 删除索引
    op.drop_index('ix_requirement_test_tasks_status')
    op.drop_index('ix_requirement_analysis_tasks_status')
    op.drop_index('ix_requirement_documents_status')
    
    # 删除表
    op.drop_table('requirement_test_tasks')
    op.drop_table('requirement_analysis_tasks')
    op.drop_table('requirement_documents') 