"""Training integration fixture; synthetic rows are test-only and never reported as model results."""
import numpy as np
import pandas as pd
import pytest
pytest.importorskip("imblearn", reason="Install project requirements to exercise training pipeline.")
pytest.importorskip("xgboost", reason="Install project requirements to exercise XGBoost candidate.")
from app.ml.data_loader import FEATURES, REQUIRED_COLUMNS
from app.ml.training import train
from app.ml.prediction import PredictionService

def test_train_writes_pipeline_and_real_metrics_for_test_fixture(tmp_path):
    rng=np.random.default_rng(23)
    labels=np.array([0]*180+[1]*30)
    rng.shuffle(labels)
    values=rng.normal(size=(len(labels),len(FEATURES)))
    values[:,1]+=labels*1.5
    data=pd.DataFrame(values,columns=FEATURES)
    data["Time"]=np.arange(len(labels),dtype=float)
    data["Amount"]=np.abs(data["Amount"])
    data["Class"]=labels
    dataset=tmp_path/"fixture.csv"
    data[REQUIRED_COLUMNS].to_csv(dataset,index=False)
    output=tmp_path/"models"
    report=train(dataset,output,seed=23)
    assert report["model_name"] in report["validation"]
    assert 0 <= report["test"]["pr_auc"] <= 1
    assert (output/"metrics.json").is_file()
    assert (output/"active_model_metadata.joblib").is_file()
    assert list(output.glob("fraud_model_*.joblib"))
    assert list(output.glob("preprocessing_*.joblib"))
    predictor=PredictionService(output)
    assert predictor.available
    prediction=predictor.predict([data.iloc[0][FEATURES].to_dict()])[0]
    assert prediction["model_version"]==report["model_version"]
    assert 0 <= prediction["fraud_probability"] <= 1
