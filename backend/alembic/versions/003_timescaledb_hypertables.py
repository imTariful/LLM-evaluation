"""Enable TimescaleDB extension and create hypertables

Revision ID: 003_timescaledb_hypertables
Revises: 002_init_tables
Create Date: 2024-02-04 02:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


revision = '003_timescaledb_hypertables'
down_revision = '002_init_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create TimescaleDB hypertables for time-series data."""
    
    # Note: TimescaleDB extensions and hypertables only work on PostgreSQL
    # For SQLite compatibility, we skip these operations but keep table structure
    
    try:
        # Try to enable TimescaleDB extension (PostgreSQL only)
        op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;")
    except Exception:
        # SQLite or other DB that doesn't support extensions
        pass
    
    # 1. Inference Traces Table (Time-series)
    op.create_table(
        'inference_traces',
        sa.Column('trace_id', sa.Uuid(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('prompt_version_id', sa.Uuid(as_uuid=True), nullable=False),
        sa.Column('inputs', sa.JSON(), nullable=False),
        sa.Column('output', sa.Text(), nullable=False),
        sa.Column('tokens_in', sa.Integer(), nullable=False),
        sa.Column('tokens_out', sa.Integer(), nullable=False),
        sa.Column('latency_ms', sa.Integer(), nullable=False),
        sa.Column('cost_usd', sa.Numeric(precision=10, scale=6), nullable=False),
        sa.Column('model', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.ForeignKeyConstraint(['prompt_version_id'], ['prompt_versions.id']),
        sa.Index('ix_inference_traces_timestamp', 'timestamp'),
        sa.Index('ix_inference_traces_prompt_version_id', 'prompt_version_id'),
    )
    
    # Try to convert to hypertable (PostgreSQL + TimescaleDB only)
    try:
        op.execute(text(
            "SELECT create_hypertable('inference_traces', 'timestamp', "
            "if_not_exists => TRUE);"
        ))
    except Exception:
        # SQLite doesn't support hypertables, but table structure is compatible
        pass
    
    # 2. Evaluation Results Table (Time-series)
    op.create_table(
        'evaluation_results',
        sa.Column('eval_id', sa.Uuid(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('trace_id', sa.Uuid(as_uuid=True), nullable=False),
        sa.Column('evaluator_id', sa.String(), nullable=False),
        sa.Column('scores', sa.JSON(), nullable=False),
        sa.Column('overall_score', sa.Float(), nullable=False),
        sa.Column('reasoning', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.ForeignKeyConstraint(['trace_id'], ['inference_traces.trace_id']),
        sa.Index('ix_evaluation_results_timestamp', 'timestamp'),
        sa.Index('ix_evaluation_results_trace_id', 'trace_id'),
        sa.Index('ix_evaluation_results_evaluator_id', 'evaluator_id'),
    )
    
    # Try to convert to hypertable (PostgreSQL + TimescaleDB only)
    try:
        op.execute(text(
            "SELECT create_hypertable('evaluation_results', 'timestamp', "
            "if_not_exists => TRUE);"
        ))
    except Exception:
        # SQLite doesn't support hypertables
        pass


def downgrade() -> None:
    """Drop hypertables and extension."""
    
    # Drop tables in reverse order of dependencies
    op.drop_table('evaluation_results')
    op.drop_table('inference_traces')
    
    # Try to drop extension (PostgreSQL only)
    try:
        op.execute("DROP EXTENSION IF NOT EXISTS timescaledb CASCADE;")
    except Exception:
        pass
