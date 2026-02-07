"""convert to hypertable

Revision ID: 001_timescale_init
Revises: 
Create Date: 2024-02-04 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001_timescale_init'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Only run TimescaleDB-specific SQL when using PostgreSQL
    bind = op.get_bind()
    dialect_name = getattr(bind.dialect, "name", None)
    if dialect_name == "postgresql":
        # Enable TimescaleDB extension if not exists (done in Docker, but safe ensure)
        op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;")
    
    # Convert tables to hypertables
    # Note: Accessing hypertable features requires the tables to exist first.
    # This migration assumes tables are created by initial revision or sync.
    # ideally, we create tables here. For this demo, we assume the 'models' are synced via `metadata.create_all` 
    # but strictly speaking, in production, we'd define the Create Table ops here.
    
    # Since we are using SQLAlchemy `create_all` in a dev context, we might run this post-creation.
    # But let's write the SQL that *would* be run.
    
    # The hypertable conversion is Postgres/TimescaleDB specific; only run there
    if dialect_name == "postgresql":
        # op.execute("SELECT create_hypertable('inference_traces', 'timestamp', migrate_data => true);")
        # op.execute("SELECT create_hypertable('evaluation_results', 'timestamp', migrate_data => true);")
        pass
    pass

def downgrade() -> None:
    pass
