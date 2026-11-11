"""Create prediction and model metadata tables."""
from alembic import op
import sqlalchemy as sa
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("transactions",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("transaction_reference", sa.String(36), nullable=False),
        sa.Column("transaction_amount", sa.Float(), nullable=False), sa.Column("transaction_time", sa.Float(), nullable=False),
        sa.Column("predicted_class", sa.Integer(), nullable=False), sa.Column("fraud_probability", sa.Float(), nullable=False),
        sa.Column("risk_level", sa.String(16), nullable=False), sa.Column("actual_class", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_transactions_transaction_reference", "transactions", ["transaction_reference"], unique=True)
    op.create_table("model_versions", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("model_name", sa.String(80), nullable=False),
        sa.Column("model_version", sa.String(40), nullable=False), sa.Column("model_path", sa.String(512), nullable=False),
        sa.Column("precision", sa.Float(), nullable=False), sa.Column("recall", sa.Float(), nullable=False), sa.Column("f1_score", sa.Float(), nullable=False),
        sa.Column("roc_auc", sa.Float(), nullable=False), sa.Column("pr_auc", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False))
    op.create_index("ix_model_versions_model_version", "model_versions", ["model_version"], unique=True)
    op.create_table("prediction_logs", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("transaction_id", sa.Integer(), nullable=False),
        sa.Column("prediction_status", sa.String(24), nullable=False), sa.Column("processing_time", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["transaction_id"], ["transactions.id"], ondelete="CASCADE"), sa.UniqueConstraint("transaction_id"))

def downgrade():
    op.drop_table("prediction_logs"); op.drop_index("ix_model_versions_model_version", table_name="model_versions"); op.drop_table("model_versions")
    op.drop_index("ix_transactions_transaction_reference", table_name="transactions"); op.drop_table("transactions")
