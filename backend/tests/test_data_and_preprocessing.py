import pandas as pd
import pytest
from app.ml.data_loader import DatasetError, FEATURES, REQUIRED_COLUMNS, dataset_summary, load_dataset
from app.ml.preprocessing import make_preprocessor

def frame():
    rows=[]
    for label in (0,1):
        row={c:0.0 for c in FEATURES}; row.update({"Time":float(label+1),"Amount":float(label+10),"Class":label}); rows.append(row)
    return pd.DataFrame(rows, columns=REQUIRED_COLUMNS)

def test_load_validates_and_summarizes(tmp_path):
    path=tmp_path/"creditcard.csv"; frame().to_csv(path,index=False)
    data=load_dataset(path)
    assert len(data)==2 and dataset_summary(data)["fraud"]==1

def test_missing_dataset_is_clear(tmp_path):
    with pytest.raises(DatasetError, match="Dataset not found"):
        load_dataset(tmp_path/"missing.csv")

def test_bad_class_is_rejected(tmp_path):
    data=frame(); data.loc[0,"Class"]=2; path=tmp_path/"bad.csv"; data.to_csv(path,index=False)
    with pytest.raises(DatasetError, match="only 0"):
        load_dataset(path)

def test_preprocessor_scales_amount_and_preserves_other_columns():
    data=frame()[FEATURES]
    transformed=make_preprocessor().fit_transform(data)
    assert transformed.shape==(2,30)
