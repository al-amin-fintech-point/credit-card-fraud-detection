import pytest
import joblib
from sklearn.dummy import DummyClassifier
from app.ml.prediction import ModelUnavailable, PredictionService
from app.ml.data_loader import FEATURES

def test_missing_model_is_explicit(tmp_path):
    service=PredictionService(tmp_path)
    assert not service.available
    with pytest.raises(ModelUnavailable): service.predict([{k:0 for k in FEATURES}])

def test_threshold_risk_mapping_with_stub(tmp_path):
    class Stub:
        def predict_proba(self, frame): return [[.1,.9] for _ in range(len(frame))]
    service=PredictionService(tmp_path, fraud_threshold=.5, high_risk_threshold=.8)
    service.model=Stub(); service.metadata={"model_version":"test"}
    result=service.predict([{k:0 for k in FEATURES}])[0]
    assert result["predicted_class"]==1 and result["risk_level"]=="HIGH RISK" and result["fraud_probability"]==.9

def test_invalid_features_fail(tmp_path):
    service=PredictionService(tmp_path); service.model=object()
    with pytest.raises(ValueError, match="Missing features"):
        service.predict([{"Amount": 2}])

def test_service_reloads_model_artifacts_written_after_startup(tmp_path):
    service=PredictionService(tmp_path)
    assert not service.available
    model=DummyClassifier(strategy="prior").fit([[0],[1]],[0,1])
    model_path=tmp_path/"trained.joblib"
    joblib.dump(model,model_path)
    joblib.dump({"model_path":model_path.name,"model_version":"fresh"},tmp_path/"active_model_metadata.joblib")
    assert service.reload_if_changed()
    assert service.metadata["model_version"]=="fresh"
