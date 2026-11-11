"""FastAPI application."""
import csv
import io
import json
import logging
import time
import uuid
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, File, Header, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from sqlalchemy import case, func
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.database import Base, engine, get_db
from app.db.models import ModelVersion, PredictionLog, Transaction
from app.ml.prediction import ModelUnavailable, PredictionService
from app.schemas import PredictionResponse, TransactionFeatures, TransactionResponse, ModelVersionResponse

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("fraud_api")
@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    _sync_model_version()
    yield


app = FastAPI(title=settings.app_name, version="1.0.0", description="Fraud risk scoring API. A model score is not a guaranteed financial decision.", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.allowed_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
predictor = PredictionService(settings.model_dir, settings.fraud_threshold, settings.high_risk_threshold)


def _sync_model_version():
    if not predictor.available: return
    try:
        report_path = settings.model_dir / "metrics.json"
        report = json.loads(report_path.read_text()) if report_path.exists() else {}
        test = report.get("test", {})
        with next(get_db()) as db:
            version = predictor.metadata.get("model_version", "unknown")
            if db.query(ModelVersion).filter_by(model_version=version).first(): return
            db.query(ModelVersion).update({"is_active": False})
            db.add(ModelVersion(model_name=predictor.metadata.get("model_name", "unknown"), model_version=version,
                model_path=str(predictor.metadata.get("model_path", "")), precision=test.get("precision", 0), recall=test.get("recall", 0),
                f1_score=test.get("f1", 0), roc_auc=test.get("roc_auc", 0), pr_auc=test.get("pr_auc", 0), is_active=True))
            db.commit()
    except Exception:
        logger.exception("Could not synchronize model metadata")


def _predict_payload(payload: dict, db: Session | None = None):
    predictor.reload_if_changed()
    started = time.perf_counter()
    try:
        result = predictor.predict([payload])[0]
    except ModelUnavailable as exc: raise HTTPException(503, str(exc)) from exc
    except ValueError as exc: raise HTTPException(422, str(exc)) from exc
    elapsed = time.perf_counter() - started
    if db is None: return result
    transaction = Transaction(transaction_reference=str(uuid.uuid4()), transaction_amount=float(payload["Amount"]), transaction_time=float(payload["Time"]),
        predicted_class=result["predicted_class"], fraud_probability=result["fraud_probability"], risk_level=result["risk_level"])
    db.add(transaction); db.flush()
    db.add(PredictionLog(transaction_id=transaction.id, prediction_status="success", processing_time=elapsed))
    db.commit(); db.refresh(transaction)
    result.update({"id": transaction.id, "transaction_reference": transaction.transaction_reference})
    return result


@app.get("/api/v1/health")
def health():
    predictor.reload_if_changed()
    return {"status": "ok", "model_available": predictor.available, "model_version": predictor.metadata.get("model_version")}


@app.post("/api/v1/predict", response_model=PredictionResponse)
def predict(payload: TransactionFeatures, db: Session = Depends(get_db)):
    return _predict_payload(payload.model_dump(), db)


@app.post("/api/v1/predict/batch")
async def predict_batch(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename or not file.filename.lower().endswith(".csv"): raise HTTPException(400, "Upload a .csv file.")
    content = await file.read(settings.max_upload_mb * 1024 * 1024 + 1)
    if len(content) > settings.max_upload_mb * 1024 * 1024: raise HTTPException(413, "CSV exceeds upload size limit.")
    try:
        decoded = content.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(decoded))
        if reader.fieldnames is None: raise ValueError("CSV must include a header row.")
        if len(reader.fieldnames) != len(set(reader.fieldnames)): raise ValueError("CSV contains duplicate column names.")
        required = set(TransactionFeatures.model_fields)
        missing = required - set(reader.fieldnames)
        if missing: raise ValueError("Missing columns: " + ", ".join(sorted(missing)))
        rows = list(reader)
        if not rows: raise ValueError("CSV contains no data rows.")
        if len(rows) > 10000: raise ValueError("CSV may contain at most 10,000 rows.")
        cleaned = [TransactionFeatures.model_validate(row).model_dump() for row in rows]
    except (UnicodeDecodeError, csv.Error, ValueError) as exc: raise HTTPException(422, f"Invalid CSV: {exc}") from exc
    except Exception as exc: raise HTTPException(422, f"Invalid CSV values: {exc}") from exc
    output = []
    for row in cleaned:
        result = _predict_payload(row, db)
        output.append({**row, **result})
    buf = io.StringIO(); writer = csv.DictWriter(buf, fieldnames=list(output[0].keys())); writer.writeheader(); writer.writerows(output)
    return Response(content=buf.getvalue(), media_type="text/csv",
                    headers={"Content-Disposition": "attachment; filename=fraud_predictions.csv"})


@app.get("/api/v1/dashboard/stats")
def dashboard_stats(db: Session = Depends(get_db)):
    total = db.query(func.count(Transaction.id)).scalar() or 0
    fraud = db.query(func.count(Transaction.id)).filter(Transaction.predicted_class == 1).scalar() or 0
    avg = db.query(func.avg(Transaction.fraud_probability)).scalar() or 0
    risk_rows = db.query(Transaction.risk_level, func.count(Transaction.id)).group_by(Transaction.risk_level).all()
    return {"total_transactions": total, "fraud_detected": fraud, "legitimate_transactions": total-fraud,
            "fraud_detection_rate": fraud / total if total else 0, "average_fraud_probability": float(avg),
            "risk_distribution": {risk: count for risk, count in risk_rows}}


@app.get("/api/v1/transactions", response_model=list[TransactionResponse])
def transactions(limit: int = Query(50, ge=1, le=500), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
    return db.query(Transaction).order_by(Transaction.created_at.desc()).offset(offset).limit(limit).all()


@app.get("/api/v1/transactions/{transaction_id}", response_model=TransactionResponse)
def transaction_detail(transaction_id: int, db: Session = Depends(get_db)):
    item = db.get(Transaction, transaction_id)
    if not item: raise HTTPException(404, "Transaction not found.")
    return item


@app.get("/api/v1/models", response_model=list[ModelVersionResponse])
def models(db: Session = Depends(get_db)):
    return db.query(ModelVersion).order_by(ModelVersion.created_at.desc()).all()


@app.get("/api/v1/models/metrics")
def model_metrics():
    path = settings.model_dir / "metrics.json"
    if not path.exists(): raise HTTPException(404, "No trained model metrics are available.")
    return json.loads(path.read_text())


@app.get("/api/v1/analytics/fraud-trends")
def fraud_trends(db: Session = Depends(get_db)):
    rows = db.query(func.date(Transaction.created_at), func.count(Transaction.id), func.sum(Transaction.predicted_class)).group_by(func.date(Transaction.created_at)).order_by(func.date(Transaction.created_at)).all()
    return [{"date": str(day), "transactions": count, "fraud": int(fraud or 0)} for day, count, fraud in rows]


@app.get("/api/v1/analytics/amounts")
def amount_analysis(db: Session = Depends(get_db)):
    band = case((Transaction.transaction_amount < 10, "0–10"),
                (Transaction.transaction_amount < 50, "10–50"),
                (Transaction.transaction_amount < 100, "50–100"),
                (Transaction.transaction_amount < 500, "100–500"), else_="500+")
    rows = db.query(band.label("amount_range"), func.count(Transaction.id),
                    func.sum(Transaction.predicted_class)).group_by("amount_range").all()
    order = {name: index for index, name in enumerate(("0–10", "10–50", "50–100", "100–500", "500+"))}
    return [{"amount_range": label, "transactions": count, "fraud": int(fraud or 0)}
            for label, count, fraud in sorted(rows, key=lambda row: order.get(row[0], 99))]


@app.post("/api/v1/model/retrain")
def retrain(x_admin_key: str | None = Header(default=None)):
    if not settings.admin_api_key or x_admin_key != settings.admin_api_key: raise HTTPException(403, "Administrator authorization required.")
    from app.ml.eda import generate_eda
    from app.ml.training import train
    from app.ml.data_loader import load_dataset
    try:
        frame = load_dataset(settings.dataset_path)
        generate_eda(frame, settings.model_dir.parent / "eda")
        report = train(settings.dataset_path, settings.model_dir)
        predictor.load(); _sync_model_version()
        return {"status": "trained", "model_version": report["model_version"], "test_metrics": report["test"]}
    except Exception as exc:
        logger.exception("Model retraining failed")
        raise HTTPException(400, f"Retraining failed: {exc}") from exc
