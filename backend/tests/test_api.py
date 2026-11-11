import asyncio
import csv
import io
import httpx
import pytest
from unittest.mock import patch
from app.main import app, predictor
from app.db.database import SessionLocal, get_db
from app.core.config import settings
from app.ml.data_loader import FEATURES, load_dataset

_REAL_SAMPLE = None

def real_sample():
    global _REAL_SAMPLE
    if not predictor.available or not settings.dataset_path.is_file():
        pytest.skip("A real trained artifact and Kaggle dataset are required for live-model API checks.")
    if _REAL_SAMPLE is None:
        frame=load_dataset(settings.dataset_path)
        _REAL_SAMPLE=[frame[frame.Class==0].iloc[0][FEATURES].to_dict(),
                      frame[frame.Class==1].iloc[0][FEATURES].to_dict()]
    return _REAL_SAMPLE

def request(method, path, **kwargs):
    async def override_db():
        with SessionLocal() as session:
            yield session

    async def run_inline(callable_, *args, **options):
        return callable_(*args, **options)

    async def run():
        app.dependency_overrides[get_db] = override_db
        try:
            async with app.router.lifespan_context(app):
                with patch("fastapi.routing.run_in_threadpool", run_inline):
                    transport=httpx.ASGITransport(app=app)
                    async with httpx.AsyncClient(transport=transport,base_url="http://testserver") as client:
                        return await client.request(method,path,**kwargs)
        finally:
            app.dependency_overrides.pop(get_db, None)
    return asyncio.run(run())

def test_health_reports_missing_model():
    response=request("GET","/api/v1/health")
    assert response.status_code==200
    assert response.json()["model_available"] is predictor.available
    if predictor.available:
        assert response.json()["model_version"]==predictor.metadata["model_version"]

def test_dashboard_stats_empty_or_valid():
    response=request("GET","/api/v1/dashboard/stats")
    assert response.status_code==200
    assert {"total_transactions","fraud_detected","fraud_detection_rate"} <= set(response.json())

def test_single_prediction_requires_model():
    if predictor.available: return
    payload={"Time":10,"Amount":5,**{f"V{i}":0 for i in range(1,29)}}
    response=request("POST","/api/v1/predict",json=payload)
    assert response.status_code==503

def test_single_prediction_succeeds_with_loaded_model(monkeypatch):
    import numpy as np
    class StubModel:
        def predict_proba(self, frame): return np.tile([.9, .1], (len(frame), 1))
    monkeypatch.setattr(predictor, "model", StubModel())
    monkeypatch.setattr(predictor, "metadata", {"model_version": "test"})
    monkeypatch.setattr(predictor, "reload_if_changed", lambda: True)
    payload={"Time":10,"Amount":5,**{f"V{i}":0 for i in range(1,29)}}
    response=request("POST","/api/v1/predict",json=payload)
    assert response.status_code==200
    assert response.json()["predicted_class"]==0
    assert response.json()["model_version"]=="test"

def test_invalid_prediction_payload_is_rejected():
    response=request("POST","/api/v1/predict",json={"Time":-1,"Amount":1})
    assert response.status_code==422

def test_retraining_requires_admin_key():
    response=request("POST","/api/v1/model/retrain")
    assert response.status_code==403

def test_batch_csv_returns_prediction_file(monkeypatch):
    import numpy as np
    from app.ml.data_loader import FEATURES
    class StubModel:
        def predict_proba(self, frame): return np.tile([.9, .1], (len(frame), 1))
    monkeypatch.setattr(predictor, "model", StubModel())
    monkeypatch.setattr(predictor, "metadata", {"model_version": "test"})
    monkeypatch.setattr(predictor, "reload_if_changed", lambda: True)
    header=",".join(FEATURES)
    values=",".join("0" for _ in FEATURES)
    response=request("POST","/api/v1/predict/batch",files={"file":("transactions.csv",f"{header}\n{values}\n","text/csv")})
    assert response.status_code==200
    assert "text/csv" in response.headers["content-type"]
    assert "fraud_probability" in response.text and "test" in response.text

def test_batch_rejects_missing_feature_columns():
    response=request("POST","/api/v1/predict/batch",files={"file":("invalid.csv","Time,Amount\n1,2\n","text/csv")})
    assert response.status_code==422

def test_trained_model_single_prediction_api():
    _, fraud=real_sample()
    response=request("POST","/api/v1/predict",json=fraud)
    assert response.status_code==200
    result=response.json()
    assert result["predicted_class"]==1
    assert result["fraud_probability"]>=.8
    assert result["model_version"]==predictor.metadata["model_version"]

def test_trained_model_batch_prediction_api():
    legitimate,fraud=real_sample()
    stream=io.StringIO()
    writer=csv.DictWriter(stream,fieldnames=FEATURES)
    writer.writeheader(); writer.writerows([legitimate,fraud])
    response=request("POST","/api/v1/predict/batch",files={"file":("real_samples.csv",stream.getvalue(),"text/csv")})
    assert response.status_code==200
    results=list(csv.DictReader(io.StringIO(response.text)))
    assert len(results)==2
    assert [int(row["predicted_class"]) for row in results]==[0,1]
    assert all(row["model_version"]==predictor.metadata["model_version"] for row in results)

def test_dashboard_can_read_real_model_metrics():
    real_sample()
    response=request("GET","/api/v1/models/metrics")
    assert response.status_code==200
    metrics=response.json()
    assert metrics["model_version"]==predictor.metadata["model_version"]
    assert metrics["model_name"]=="xgboost"
    assert metrics["test"]["pr_auc"]>0

def test_active_model_version_is_available_to_dashboard():
    real_sample()
    response=request("GET","/api/v1/models")
    assert response.status_code==200
    active=[model for model in response.json() if model["is_active"]]
    assert len(active)==1
    assert active[0]["model_version"]==predictor.metadata["model_version"]
