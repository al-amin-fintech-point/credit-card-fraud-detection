"""API request/response schemas."""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, create_model

_fields = {"Time": (float, Field(ge=0)), "Amount": (float, Field(ge=0))}
_fields.update({f"V{i}": (float, ...) for i in range(1, 29)})
TransactionFeatures = create_model("TransactionFeatures", __config__=ConfigDict(extra="forbid"), **_fields)


class PredictionResponse(BaseModel):
    id: int | None = None
    transaction_reference: str | None = None
    predicted_class: int
    fraud_probability: float
    risk_level: str
    model_version: str


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    transaction_reference: str
    transaction_amount: float
    transaction_time: float
    predicted_class: int
    fraud_probability: float
    risk_level: str
    actual_class: int | None
    created_at: datetime


class ModelVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    model_name: str
    model_version: str
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    pr_auc: float
    created_at: datetime
    is_active: bool
