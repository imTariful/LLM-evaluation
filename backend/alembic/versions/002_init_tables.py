"""init_tables

Revision ID: 002_init_tables
Revises: 001_timescale_init
Create Date: 2024-02-04 01:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Uuid, JSON
# from sqlalchemy.dialects import postgresql
# from pgvector.sqlalchemy import Vector (Not supported in SQLite easily without extension)


# revision identifiers, used by Alembic.
revision = '002_init_tables'
down_revision = '001_timescale_init'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Prompts
    op.create_table('prompts',
        sa.Column('id', sa.Uuid(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_prompts_name'), 'prompts', ['name'], unique=True)

    # 2. Prompt Versions
    op.create_table('prompt_versions',
        sa.Column('id', sa.Uuid(as_uuid=True), nullable=False),
        sa.Column('prompt_id', sa.Uuid(as_uuid=True), nullable=False),
        sa.Column('version', sa.String(), nullable=False),
        sa.Column('system_template', sa.String(), nullable=True),
        sa.Column('user_template', sa.String(), nullable=False),
        sa.Column('model_config', sa.JSON(), nullable=False),
        sa.Column('author', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['prompt_id'], ['prompts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 3. Knowledge Base (pgvector -> JSON for fallback)
    op.create_table('knowledge_base',
        sa.Column('id', sa.Uuid(as_uuid=True), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('embedding', sa.JSON(), nullable=True), # Fallback for vector
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 4. Inference Traces
    op.create_table('inference_traces',
        sa.Column('id', sa.Uuid(as_uuid=True), nullable=False),
        sa.Column('prompt_version_id', sa.Uuid(as_uuid=True), nullable=True),
        sa.Column('inputs', sa.JSON(), nullable=False),
        sa.Column('output', sa.String(), nullable=False),
        sa.Column('model', sa.String(), nullable=False),
        sa.Column('provider', sa.String(), nullable=False),
        sa.Column('tokens_in', sa.Integer(), nullable=True),
        sa.Column('tokens_out', sa.Integer(), nullable=True),
        sa.Column('latency_ms', sa.Integer(), nullable=True),
        sa.Column('cost_usd', sa.Float(), nullable=True),
        sa.Column('session_id', sa.String(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['prompt_version_id'], ['prompt_versions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 5. Evaluation Results
    op.create_table('evaluation_results',
        sa.Column('id', sa.Uuid(as_uuid=True), nullable=False),
        sa.Column('trace_id', sa.Uuid(as_uuid=True), nullable=False),
        sa.Column('evaluator_id', sa.String(), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('metrics', sa.JSON(), nullable=False),
        sa.Column('reasoning', sa.String(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['trace_id'], ['inference_traces.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('evaluation_results')
    op.drop_table('inference_traces')
    op.drop_table('knowledge_base')
    op.drop_table('prompt_versions')
    op.drop_index(op.f('ix_prompts_name'), table_name='prompts')
    op.drop_table('prompts')
