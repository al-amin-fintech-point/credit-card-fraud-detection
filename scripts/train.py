"""Validate data, generate EDA, and train model candidates."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.ml.data_loader import load_dataset, dataset_summary
from app.ml.eda import generate_eda
from app.ml.training import train

def main():
    dataset = ROOT / "data" / "raw" / "creditcard.csv"
    frame = load_dataset(dataset)
    print("Dataset summary:", dataset_summary(frame))
    print("EDA charts:", generate_eda(frame, ROOT / "artifacts" / "eda"))
    report = train(dataset, ROOT / "artifacts" / "models")
    print(f"Selected {report['model_name']} ({report['model_version']})")
    print("Held-out test metrics:", report["test"])

if __name__ == "__main__": main()
